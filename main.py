import base64
import datetime
import math
import os
import pygame
import pytz
import re
import requests
import sys
from dotenv import load_dotenv
from io import BytesIO
from itertools import cycle
from PIL import Image, ImageDraw, ImageFont


def get_text_dimensions(text_string, test_font):
    ascent, descent = test_font.getmetrics()
    text_width = test_font.getmask(text_string).getbbox()[2] or 0
    text_height = test_font.getmask(text_string).getbbox()[3] + descent or 0
    return text_width, text_height


def hex_to_rgb(value):
    value = value.lstrip('#')
    lv = len(value)
    return tuple(int(value[i:i + lv // 3], 16) for i in range(0, lv, lv // 3))


def find_event_info(included_data, event_id):
    return next((item for item in included_data if item['type'] == 'Event' and item['id'] == event_id), None)


def fetch_event_instances():
    response = requests.get(f"{api_base_url}event_instances?where[tag_ids]={regular_event_id}&include=event,attachments&filter=future&order=starts_at", headers=headers)
    if response.status_code == 200:
        return response.json()
    else:
        print('Failed to fetch event instances:', response.status_code, response.text)
        return []


def fetch_always_show_event_instances():
    response = requests.get(f"{api_base_url}event_instances?where[tag_ids]={always_show_id}&include=event,attachments&filter=future&order=starts_at", headers=headers)
    if response.status_code == 200:
        return response.json()
    else:
        print('Failed to fetch event instances:', response.status_code, response.text)
        return []


def fetch_event_image(image_url):
    if image_url:
        image_response = requests.get(image_url)
        if image_response.status_code == 200:
            return image_response.content
    return None


def draw_event(background_image, title, start_datetime, end_datetime, description, overlay):
    image = Image.new('RGBA', bottom_right)
    draw = ImageDraw.Draw(image, 'RGBA')
    event_image = Image.open(BytesIO(background_image))
    event_image = event_image.resize((event_image_output_width, event_image_output_height))
    draw.rectangle((top_left, bottom_right), fill=background_color)
    image.paste(event_image, inset_top_left)
    image.paste(overlay, top_left, mask=overlay)

    title = title.upper()
    same_day = (start_datetime.date() == end_datetime.date())
    month_display = start_datetime.strftime('%b').upper()
    day_display = start_datetime.strftime('%-d')
    day_of_week_display = start_datetime.strftime('%A').upper()

    clean = re.compile('<.*?>|\n|\r\n')
    description_display = re.sub(clean, '', description).lstrip().rstrip().upper()

    time_display_start = f"{start_datetime.strftime('%-I:%M %p')} -"
    time_display_end = f"{end_datetime.strftime('%-I:%M %p')}"
    if not same_day:
        time_display_end_date = f"{end_datetime.strftime('%b %d')}"
    else:
        time_display_end_date = ''

    title_display_length, title_display_height = get_text_dimensions(title, font_title)
    title_display_x = ((event_image_output_width - title_display_length) // 2) + event_image_margin_left
    title_display_y = ((event_image_margin_top - title_display_height) // 2)
    draw.text((title_display_x, title_display_y), title, font=font_title, fill=text_color)

    if description_display:
        description_display_length, description_display_height = \
            get_text_dimensions(description_display, font_description)
        description_display_x = ((event_image_output_width - description_display_length) // 2) + event_image_margin_left
        description_display_y = ((event_image_margin_bottom - description_display_height) // 2) + event_image_inset_bottom
        draw.text((description_display_x, description_display_y),
                  description_display, font=font_description, fill=text_color)

    day_of_week_length = draw.textlength(day_of_week_display, font=font_day_of_week) or 0
    day_of_week_center_position = ((calendar_width - day_of_week_length) // 2) + calendar_left
    draw.text((day_of_week_center_position, 28), day_of_week_display, font=font_day_of_week, fill=text_color)

    day_display_length = draw.textlength(day_display, font=font_day) or 0
    day_display_position = ((calendar_width - day_display_length) // 2) + calendar_left
    draw.text((day_display_position, 43), day_display, font=font_day, fill=text_color)

    month_display_length = draw.textlength(month_display, font=font_month) or 0
    month_center_position = ((calendar_width - month_display_length) // 2) + calendar_left
    draw.text((month_center_position, 195), month_display, font=font_month, fill=text_color)

    time_display_length = draw.textlength(time_display_start, font=font_time) or 0
    time_display_center_position = ((event_image_margin_right - time_display_length) // 2) + event_image_inset_right
    draw.text((time_display_center_position, 290), time_display_start, font=font_time, fill=text_color)

    time_display_end_length = draw.textlength(time_display_end, font=font_time) or 0
    time_display_end_center_position = ((event_image_margin_right - time_display_end_length) // 2) + event_image_inset_right
    draw.text((time_display_end_center_position, 340), time_display_end, font=font_time, fill=text_color)

    if time_display_end_date:
        time_display_end_date_length = draw.textlength(time_display_end_date, font=font_time) or 0
        time_display_end_date_center_position = ((event_image_margin_right - time_display_end_date_length) // 2) + event_image_inset_right
        draw.text((time_display_end_date_center_position, 390), time_display_end_date, font=font_time, fill=text_color)

    return image


def draw_overlay():
    overlay_image = Image.new('RGBA', bottom_right)
    draw = ImageDraw.Draw(overlay_image, 'RGBA')
    draw.rectangle((inset_top_left, inset_bottom_right), fill=None, outline=outline_color, width=9)
    draw.rounded_rectangle((calendar_top_left, calendar_bottom_right), radius=8, fill=None, outline=text_color, width=3)
    logo_image = Image.open(logo_path)
    overlay_image.paste(logo_image, (event_image_inset_left + logo_margin_top_left, event_image_inset_top + logo_margin_top_left), mask=logo_image)
    return overlay_image


def build_event_images(events, overlay, always_show = False):
    for event in events['data']:
        event_info = find_event_info(events['included'], event['relationships']['event']['data']['id'])
        if 'image_url' in event_info['attributes']:
            background_image = fetch_event_image(event_info['attributes']['image_url'])
            description = event_info['attributes']['description'] or ''
            name = event_info['attributes']['name'] or ''
            start_datetime = datetime.datetime.fromisoformat(event['attributes']['starts_at']).astimezone(tz)
            end_datetime = datetime.datetime.fromisoformat(event['attributes']['ends_at']).astimezone(tz)
            if background_image and (always_show or start_datetime <= event_date_limit):
                image = draw_event(background_image, name, start_datetime, end_datetime, description, overlay)
                images.append(image)


def restart_program():
    os.execl(sys.executable, 'python', *sys.argv)


def main():
    pygame.init()
    screen = pygame.display.set_mode(bottom_right, pygame.FULLSCREEN)
    featured_events = fetch_always_show_event_instances()
    events = fetch_event_instances()
    overlay = draw_overlay()
    build_event_images(featured_events, overlay, True)
    build_event_images(events, overlay)
    app_start_time = pygame.time.get_ticks()
    running = True
    clock = pygame.time.Clock()
    last_update_time = pygame.time.get_ticks()
    if images:
        image_cycle = cycle(images)
        current_image = next(image_cycle)
        next_image = None
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.KEYDOWN:
                    running = False
            current_time = pygame.time.get_ticks()
            if (current_time - app_start_time) >= restart_time:
                pygame.quit()
                restart_program()
            if current_time - last_update_time >= image_display_time:
                next_image = next(image_cycle)
                last_update_time = current_time
            if next_image:
                elapsed = current_time - last_update_time
                progress = elapsed / transition_time
                if progress >= 1:
                    current_image = next_image
                    next_image = None
                else:
                    current_pygame_image = \
                        pygame.image.fromstring(current_image.tobytes(), current_image.size, current_image.mode)
                    next_pygame_image = pygame.image.fromstring(next_image.tobytes(), next_image.size, next_image.mode)
                    offset = int(output_image_width * progress)
                    screen.blit(current_pygame_image, (-offset, 0))
                    screen.blit(next_pygame_image, (output_image_width - offset, 0))
            else:
                pygame_image = pygame.image.fromstring(current_image.tobytes(), current_image.size, current_image.mode)
                screen.blit(pygame_image, top_left)
            pygame.display.flip()
            clock.tick(60)
    pygame.quit()


# import config from env
try:
    load_dotenv()
    application_id = os.getenv('application_id')
    application_secret = os.getenv('application_secret')
    always_show_id = os.getenv('always_show_id')
    regular_event_id = os.getenv('regular_event_id')
    api_base_url = os.getenv('api_base_url', 'https://api.planningcenteronline.com/calendar/v2/')
    logo_path = os.getenv('logo_path', 'images/logo.png')
    splash_path = os.getenv('splash_path', 'images/splash.png')
    background_color = hex_to_rgb(os.getenv('background_color', '#442663'))
    outline_color = os.getenv('outline_color', 'black')
    text_color = os.getenv('text_color', 'white')
    image_display_time = int(os.getenv('image_display_time',  12000))
    allow_days_in_future = int(os.getenv('allow_days_in_future',  15))
    transition_time = int(os.getenv('transition_time',  900))
    restart_time = int(os.getenv('restart_time',  7200000))
    configured_timezone = os.getenv('configured_timezone', 'America/New_York')
    output_image_width = int(os.getenv('output_image_width',  1920))
    output_image_height = int(os.getenv('output_image_height',  1080))
    event_image_source_width = int(os.getenv('event_image_source_width',  1920))
    event_image_source_height = int(os.getenv('event_image_source_height',  1080))
    event_image_output_width = int(os.getenv('event_image_output_width',  1536))
    event_image_margin_left = int(os.getenv('event_image_margin_left',  108))
except:
    print('Unable to load environment variables')
    exit(1)

try:
    # static calculations
    output_display_ratio = output_image_width / output_image_height
    event_image_ratio = event_image_source_width / event_image_source_height
    event_image_output_height = math.floor(event_image_output_width // event_image_ratio)
    event_image_margin_top = (output_image_height - event_image_output_height) // 2
    event_image_margin_bottom = event_image_margin_top
    event_image_margin_right = output_image_width - event_image_output_width - event_image_margin_left
    event_image_offset_right = 3
    event_image_inset_top = event_image_margin_top
    event_image_inset_bottom = event_image_margin_top + event_image_output_height
    event_image_inset_left = event_image_margin_left
    event_image_inset_right = event_image_margin_left + event_image_output_width
    inset_top_left = (event_image_inset_left, event_image_inset_top)
    inset_top_right = (event_image_inset_right, event_image_inset_top)
    inset_bottom_left = (event_image_inset_left, event_image_inset_bottom)
    inset_bottom_right = (event_image_inset_right, event_image_inset_bottom)
    top_left = (0, 0)
    top_right = (0, output_image_height)
    bottom_left = (output_image_width, 0)
    bottom_right = (output_image_width, output_image_height)
    calendar_left = event_image_inset_right + 21
    calendar_right = output_image_width - 24
    calendar_width = calendar_right - calendar_left
    calendar_top_left = calendar_left, 18
    calendar_bottom_right = calendar_right, 275
    logo_margin_top_left = 15
except:
    print('Unable to load calculate dimensions')
    exit(1)

try:
    # Fonts
    font_time = ImageFont.truetype('fonts/dejavu-sans/DejaVuSans-Bold.ttf', 44)
    font_day_of_week = ImageFont.truetype('fonts/dejavu-sans/DejaVuSans-Bold.ttf', 31)
    font_day = ImageFont.truetype('fonts/dejavu-sans/DejaVuSans-Bold.ttf', 160)
    font_month = ImageFont.truetype('fonts/dejavu-sans/DejaVuSans-Bold.ttf', 64)
    font_description = ImageFont.truetype('fonts/dejavu-sans/DejaVuSans.ttf', 34)
    font_title = ImageFont.truetype('fonts/dejavu-sans/DejaVuSans-Bold.ttf', 80)
except:
    print('Unable to load fonts')
    exit(1)

try:
    # Init
    images = []
    headers = {
        'Authorization':
            f'Basic {base64.b64encode(f"{application_id}:{application_secret}".encode("utf-8")).decode("utf-8")}',
        'Content-Type':
            'application/json'
    }
    tz = pytz.timezone(configured_timezone)
    event_date_limit = datetime.datetime.now(tz) + datetime.timedelta(days=allow_days_in_future)
except:
    print('Unable to init main vars')
    exit(1)

if __name__ == "__main__":
    main()
sys.exit()
