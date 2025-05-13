import asyncio

import traceback

import json, inspect
import os, time, platform, threading
import uuid
from datetime import datetime

from crosscutting.logging.app_logger_config import AppLoggerConfigsParser


class StructuredLog:

    def __init__(self,
                 level: str,
                 source: str,
                 message: str,
                 data,
                 corr_id: str):
        self.lvl = level
        self.msg = message
        self.src = source
        self.data = data
        self.timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]
        self.corr_id = corr_id

class AppLogger:
    """
    Test logger object class. Formats, prints, and saves messages to local logs folder.
    """

    CONFIGS = AppLoggerConfigsParser.parse()

    LOG_SAVE_PATH = 'logs'                          # :str: Default log saving location.
    HEADER_SIZE = 80                                # :int: Length of the headers.
    # WRAPPER = textwrap.TextWrapper(width=20000)     # :TextWrapper: Maximum amount of characters per line.
    TIMEZONE = ''
    ANSI = {                                        # :dict: ANSI decorations for terminal.
        'magenta': '\u001b[35m',
        'yellow': '\u001b[33m',
        'red': '\u001b[31m',
        'green': '\u001b[32m',
        'cyan': '\u001b[36m',
        'gray': '\u001b[37m',
        'blue': '\u001b[34m',
        'orange': '\u001b[38;2;255;165;0m',
        'dark_orange': '\u001b[38;2;204;102;0m',
        'bg_black': '\u001b[40m',
        'bg_red': '\u001b[41m',
        'bg_green': '\u001b[42m',
        'bg_yellow': '\u001b[43m',
        'bg_blue': '\u001b[44m',
        'bg_magenta': '\u001b[45m',
        'bg_cyan': '\u001b[46m',
        'bg_white': '\u001b[47m',
        'bold': '\u001b[1m',
        'underline': '\u001b[4m',
        'reversed': '\u001b[7m',
        'default': '\u001b[0m'
    }

    CORRELATION_ID = None

    @classmethod
    def _log_message(cls, msg: str, level: str, color: str, print_on_screen: bool, say: bool, data: dict = None,
                     exception: Exception = None, source_level: int = 3, source=None):
        """
        Generic method to handle logging logic.
        """
        if not cls.CONFIGS.is_structured:
            color_code, default, reverse = cls.ANSI.get(color), cls.ANSI.get('default'), cls.ANSI.get('reversed')
            color_code = color_code if color_code else default
            level = level[:4]
            msg_ansi = f"{color_code}{reverse}{cls.__get_now('%H:%M:%S.%f')[:-4]} {default} {color_code}{reverse} {level} {default} {color_code}{reverse} {cls.get_source(source_level) if not source else source} {default} {color_code}{msg}{default}"

            if exception:
                msg_ansi += f"\n{color_code}"
                msg_ansi += "\n".join(traceback.format_exception(type(exception), exception, exception.__traceback__))
                msg_ansi += f"{default}"

            cls.log(msg_ansi, print_on_screen=print_on_screen, data=data)
            if say:
                cls.__say(msg)
        else:
            cls.log(msg, level=level, print_on_screen=print_on_screen, data=data)
            if exception:
                stack_trace = "".join(traceback.format_exception(type(exception), exception, exception.__traceback__))
                cls.log(stack_trace, print_on_screen=print_on_screen)

    @classmethod
    def highlight(cls, msg: str, print_on_screen: bool = True, say: bool = False, data: dict = None):
        cls._log_message(msg, level="INFO", color="magenta", print_on_screen=print_on_screen, say=say, data=data)

    @classmethod
    def debug(cls, msg: str, print_on_screen: bool = True, say: bool = False, data: dict = None):
        cls._log_message(msg, level="DEBUG", color="gray", print_on_screen=print_on_screen, say=say, data=data)

    @classmethod
    def info(cls, msg: str, print_on_screen: bool = True, say: bool = False, data: dict = None):
        cls._log_message(msg, level="INFO", color="", print_on_screen=print_on_screen, say=say, data=data)

    @classmethod
    def warn(cls, msg: str, print_on_screen: bool = True, say: bool = False, data: dict = None):
        cls._log_message(msg, level="WARN", color="yellow", print_on_screen=print_on_screen, say=say, data=data)

    @classmethod
    def error(cls, msg: str, exception: Exception = None, print_on_screen: bool = True, say: bool = False, data: dict = None):
        cls._log_message(msg, level="ERROR", color="red", print_on_screen=print_on_screen, say=say, data=data, exception=exception)

    @classmethod
    def critical(cls, msg: str, exception: Exception = None, print_on_screen: bool = True, say: bool = False, data: dict = None):
        cls._log_message(msg, level="CRITICAL", color="dark_orange", print_on_screen=print_on_screen, say=say, data=data, exception=exception)

    @classmethod
    def log_timeit(cls, msg: str, print_on_screen: bool = True, data=None, source=None):
        cls._log_message(msg, level="INFO", color="cyan", print_on_screen=print_on_screen, say=False, data=data, source=source)

    @classmethod
    def empty_line(cls):
        if not cls.CONFIGS.is_structured:
            print()

    @classmethod
    def __say(cls, msg: str):
        if platform.system() == 'Darwin':
            msg = msg\
                .replace(':', ' ')\
                .replace('-', ' ')\
                .replace('<', ' ')\
                .replace('>', ' ')\
                .replace('/', ' of ')
            threading.Thread(target=lambda a: os.system(f'say "{msg}"'), args=('',)).start()

    @classmethod
    def underline(cls, msg: str) -> str:
        """
        Formats provided string with underline.
        :param msg: Message to be formatted.
        :return: String containing formatted message.
        """

        return f"{cls.ANSI.get('underline')}{msg}{cls.ANSI.get('default')}"

    @classmethod
    def bold(cls, msg: str) -> str:
        """
        Formats provided string with bold.
        :param msg: Message to be formatted.
        :return: String containing formatted message.
        """

        return f"{cls.ANSI.get('bold')}{msg}{cls.ANSI.get('default')}"

    @classmethod
    def invert(cls, msg: str) -> str:
        """
        Formats provided string with inverted color.
        :param msg: Message to be formatted.
        :return: String containing formatted message.
        """

        return f"{cls.ANSI.get('invert')}{msg}{cls.ANSI.get('default')}"

    @classmethod
    def paint_status(cls, msg: str, success: bool) -> str:
        """
        Colors a given message green or red depending on success factor.
        :param msg: Message to be colored.
        :param success: Success factor.
        :return: String containing formatted message.
        """

        color = 'green' if success else 'red'
        return f"{cls.ANSI.get(color)}{msg}{cls.ANSI.get('default')}"

    @classmethod
    def paint_status_bg(cls, msg: str, success: bool) -> str:
        """
        Colors a given message background green or red depending on success factor.
        :param msg: Message to be colored.
        :param success: Success factor.
        :return: String containing formatted message.
        """

        color = 'green' if success else 'red'
        return f"{cls.ANSI.get(color)}{cls.ANSI.get('reversed')}{msg}{cls.ANSI.get('default')}"

    @classmethod
    def get_status_string(cls, status: bool) -> str:
        """
        Returns a standard stylized status indicating string.
        :param status: Success factor.
        :return: String containing status indicator.
        """

        # If status is positive (true), returns standard stylized 'test passed' string.
        if status: return cls.paint_status('(+)', True)

        # If status is negative (false), returns standard stylized 'test failed' string.
        else: return cls.paint_status('(-)', False)

    @classmethod
    def log(cls, line, level: str=None, print_on_screen=True, ignore_wrap=False, data=None, source=None):
        """
        Trims, prints and saves log lines to memory.
        :param line: Line to be analyzed.
        :param print_on_screen: Flag to whether print line on screen or only on file.
        :param ignore_wrap: Flag to ignore line wrapper if needed.
        :return: void.
        """
        cls.log_structured(line, level, data, source)

    @classmethod
    def log_structured(cls, line, level, data=None, source=None):
        if not cls.CONFIGS.is_structured:
            print(line)
            if data is None: return
            if isinstance(data, str):
                print(data)
            else:
                print(json.dumps(data, indent=4, default=str, ensure_ascii=False))
        else:
            log = StructuredLog(
                level=level,
                source=cls.get_source(5) if source is None else source,
                message=line,
                data=data,
                corr_id=cls.CORRELATION_ID
            )
            print(json.dumps(log.__dict__, default=str, ensure_ascii=False))

    # @classmethod
    # def save_logs(cls):
    #     """
    #     Saves acquired log lines to .txt file at default log file location with auto generated name.
    #     :return: void.
    #     """
    #
    #     # Removes oldest log file if maximum threshold has been reached.
    #     path = cls.LOG_SAVE_PATH
    #     log_files = [f"{path}/{name}" for name in os.listdir(path) if os.path.isfile(os.path.join(path, name))]
    #     no_of_logs = len(log_files)
    #     if no_of_logs >= cls.MAXIMUM_LOG_FILES_STORED:
    #         oldest_file = min(log_files, key=os.path.getctime)
    #         os.remove(oldest_file)
    #
    #     # Saves current log lines in new log file.
    #     log_path_and_name = f'{path}/{datetime.now().strftime("%Y-%m-%d_%H-%M-%S")}.txt'
    #     strings_to_replace = [v for k, v in cls.ANSI.items()]
    #     with open(log_path_and_name, "w") as txt_file:
    #         for line in cls.LOG_STORAGE:
    #             for reps in strings_to_replace:
    #                 line = line.replace(reps, '')
    #             txt_file.write(''.join(line) + '\n')

    @classmethod
    def print_header(cls, content):
        """
        Prints main header on log screen.
        :param content (string): Text to be displayed on main header.
        :return: void
        """

        if not cls.CONFIGS.is_structured:
            color, default = cls.ANSI.get('magenta'), cls.ANSI.get('default')
            size = cls.HEADER_SIZE
            cls.log('', ignore_wrap=True)
            main = '{' + "".join([' ' for x in range(int(size/2)-int((len(content)/2)))]) + content
            main += "".join([' ' for x in range(size-len(main))]) + '}'
            upper_line = ' /' + "".join(['=' for x in range(len(main)-4)]) + '\\'
            lower_line = ' \\' + "".join(['=' for x in range(len(main)-4)]) + '/'
            cls.log(f'{cls.ANSI.get("bold")}{color}{upper_line}\n{main}\n{lower_line}{default}', ignore_wrap=True)
            # cls.log('', ignore_wrap=True)

    @classmethod
    def __get_now(cls, formatting: str = '%H:%M:%S') -> str:
        """
        Returns current formatted time in configured timezone.
        :param formatting: Time format.
        :return: String containing current time.
        """

        if cls.TIMEZONE == 'UTC':
            return f" {datetime.utcnow().strftime(formatting)}:UTC "
        else:
            return f" {datetime.now().strftime(formatting)} "

    @classmethod
    def get_source(cls, level=2) -> str:
        try:
            frame = inspect.currentframe()
            for _ in range(level):
                if frame is None:
                    return "N.A."
                frame = frame.f_back

            if frame is None:
                return "N.A."

            locals_key = "self" if "self" in frame.f_locals else "cls"
            obj = frame.f_locals.get(locals_key)
            if obj is None:
                return "N.A."

            the_module = obj.__class__.__module__
            the_class = obj.__class__.__name__
            the_method = frame.f_code.co_name

            if cls.CONFIGS.short_source:
                the_module = ".".join([x[:1] for x in the_module.split(".")])

            source = f"{the_module}.{the_class}.{the_method}()"

            return source if cls.CONFIGS.is_structured else source.ljust(cls.CONFIGS.source_length)[:cls.CONFIGS.source_length]
        except Exception:
            return "N.A."

    @classmethod
    def timeit(cls):
        """
        Decorator to log execution time for both synchronous and asynchronous functions.
        """

        def decorator(method):
            if asyncio.iscoroutinefunction(method):
                async def async_measure(*args, **kw):
                    ts = time.time()
                    result = await method(*args, **kw)
                    te = time.time()
                    cls._log_execution_time(method, ts, te)
                    return result

                return async_measure
            else:
                def sync_measure(*args, **kw):
                    ts = time.time()
                    result = method(*args, **kw)
                    te = time.time()
                    cls._log_execution_time(method, ts, te)
                    return result

                return sync_measure

        return decorator

    @classmethod
    def _log_execution_time(cls, method, start_time, end_time):
        """
        Logs the execution time of a method.
        """
        elapsed_time = end_time - start_time
        elapsed_str = f"{round(elapsed_time, 3)}s" if elapsed_time < 60 else f"{int(elapsed_time // 60)}m {round(elapsed_time % 60, 3)}s"
        method_module = inspect.getmodule(method).__name__
        method_class = method.__qualname__
        if not cls.CONFIGS.is_structured and cls.CONFIGS.short_source:
            method_module = ".".join([x[:1] for x in method_module.split(".")])
        source = f"{method_module}.{method_class}() <timeit>".ljust(cls.CONFIGS.source_length)[:cls.CONFIGS.source_length]
        if not cls.CONFIGS.is_structured:
            cls.log_timeit(f"Elapsed: {elapsed_str}.", source=source)
        else:
            cls.log_timeit(f"Elapsed: {elapsed_str}.", source=source, data={"seconds": round(elapsed_time, 3)})

    @classmethod
    def set_correlation_id(cls, corr_id: str):
        if corr_id is not None and len(corr_id)>0:
            cls.CORRELATION_ID = corr_id
        else:
            cls.CORRELATION_ID = uuid.uuid4()