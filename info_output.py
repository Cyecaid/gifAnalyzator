from gif_parser import GifParser


def print_file_description(parser: GifParser):
    result = f"{parser.screen_descriptor}\n"
    return result


def print_frames_description(parser: GifParser):
    result = f"{print_file_description(parser)}\n"
    for i, frame in enumerate(parser.frames, start=1):
        result += f"* Кадр {i}:\n"
        result += f"{frame}\n"
        if frame.graphic_control_extension:
            result += f"{frame.graphic_control_extension}\n"
        if frame.plain_text_ext:
            result += f"{frame.plain_text_ext}\n"
        if frame.application_ext:
            result += f"{frame.application_ext}\n"
        if frame.comment_ext:
            result += f"{frame.comment_ext}\n"
        result += "\n"
    return result
