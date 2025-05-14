import asyncio
import traceback
import json, inspect
import os, time, platform, threading
import uuid
from datetime import datetime

from crosscutting.logging.app_logger_config import AppLoggerConfigsParser, LogLevel


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

    TIMEZONE = ""

    ANSI = {
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

    MIN_LEVEL_BY_PREFIX_ITEMS = None

    LOG_LEVELS = {
        LogLevel.DEBUG: 0,
        LogLevel.INFO: 1,
        LogLevel.WARN: 2,
        LogLevel.ERROR: 3,
        LogLevel.CRITICAL: 4
    }

    LOG_LEVELS_CACHE = {}

    CORRELATION_ID = None

    @classmethod
    def _log_message(cls, msg: str, level: LogLevel, color: str, say: bool, data: dict = None,
                     exception: Exception = None, source_level: int = 3, source=None):
        """
        Generic method to handle logging logic.
        """

        source = cls._get_source(source_level) if not source else source

        if cls._should_filter_source(source, level):
            return

        if not cls.CONFIGS.is_structured:
            color_code, default, reverse = cls.ANSI.get(color), cls.ANSI.get('default'), cls.ANSI.get('reversed')
            color_code = color_code if color_code else default
            level = level.value[:4]
            msg_ansi = f"{color_code}{reverse}{cls._get_now('%H:%M:%S.%f')[:-4]} {default} {color_code}{reverse} {level} {default} {color_code}{reverse} {source} {default} {color_code}{msg}{default}"

            if exception:
                msg_ansi += f"\n{color_code}"
                msg_ansi += "".join(traceback.format_exception(type(exception), exception, exception.__traceback__))
                msg_ansi += f"{default}"

            cls._log(msg_ansi, data=data)
            if say:
                cls._say(msg)
        else:
            cls._log(msg, source=source, level=level, data=data)
            if exception:
                stack_trace = "".join(traceback.format_exception(type(exception), exception, exception.__traceback__))
                cls._log(stack_trace)

    @classmethod
    def _log(cls, msg: str, level: LogLevel=None, data=None, source=None):
        """
        Trims, prints and saves log lines to memory.
        :param msg: Line to be analyzed.
        :return: void.
        """
        if cls.CONFIGS.is_structured:
            log = StructuredLog(
                level=level.value if level else "N.A.",
                source=source if source else "N.A.",
                message=msg,
                data=data,
                corr_id=cls.CORRELATION_ID
            )
            print(json.dumps(log.__dict__, default=str, ensure_ascii=False))
        else:
            print(msg)
            if data is None: return
            if isinstance(data, str):
                print(data)
            else:
                print(json.dumps(data, indent=4, default=str, ensure_ascii=False))

    @classmethod
    def _should_filter_source(cls, source: str, level: LogLevel) -> bool:
        cached_level = cls.LOG_LEVELS_CACHE.get(source)
        min_level = cls.CONFIGS.min_level

        if cached_level is not None:
            min_level = cached_level
        elif any(source.startswith(prefix) for prefix in cls.CONFIGS.min_level_by_prefix.keys()):
            if not cls.MIN_LEVEL_BY_PREFIX_ITEMS:
                cls.MIN_LEVEL_BY_PREFIX_ITEMS = sorted(cls.CONFIGS.min_level_by_prefix.items(), key=lambda item: len(item[0]), reverse=True)
            for prefix, config_level in cls.MIN_LEVEL_BY_PREFIX_ITEMS:
                if source.startswith(prefix):
                    min_level = config_level
                    cls.LOG_LEVELS_CACHE[source] = config_level
                    break
        else:
            cls.LOG_LEVELS_CACHE[source] = min_level

        if cls.LOG_LEVELS[level] < cls.LOG_LEVELS[min_level]:
            return True
        return False

    @classmethod
    def highlight(cls, msg: str, say: bool = False, data: dict = None):
        cls._log_message(msg, level=LogLevel.INFO, color="magenta", say=say, data=data)

    @classmethod
    def debug(cls, msg: str, say: bool = False, data: dict = None):
        cls._log_message(msg, level=LogLevel.DEBUG, color="gray", say=say, data=data)

    @classmethod
    def info(cls, msg: str, say: bool = False, data: dict = None):
        cls._log_message(msg, level=LogLevel.INFO, color="", say=say, data=data)

    @classmethod
    def warn(cls, msg: str, say: bool = False, data: dict = None):
        cls._log_message(msg, level=LogLevel.WARN, color="yellow", say=say, data=data)

    @classmethod
    def error(cls, msg: str, exception: Exception = None, say: bool = False, data: dict = None):
        cls._log_message(msg, level=LogLevel.ERROR, color="red", say=say, data=data, exception=exception)

    @classmethod
    def critical(cls, msg: str, exception: Exception = None, say: bool = False, data: dict = None):
        cls._log_message(msg, level=LogLevel.CRITICAL, color="dark_orange", say=say, data=data, exception=exception)

    @classmethod
    def _log_timeit(cls, msg: str, data=None, source=None):
        cls._log_message(msg, level=LogLevel.INFO, color="cyan", say=False, data=data, source=source)

    @classmethod
    def _say(cls, msg: str):
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
    def print_header(cls, content):
        """
        Prints main header on log screen.
        :param content (string): Text to be displayed on main header.
        :return: void
        """

        if not cls.CONFIGS.is_structured:
            color, default = cls.ANSI.get('magenta'), cls.ANSI.get('default')
            size = cls.CONFIGS.header['size']
            cls._log('')
            main = '{' + "".join([' ' for x in range(int(size/2)-int((len(content)/2)))]) + content
            main += "".join([' ' for x in range(size-len(main))]) + '}'
            upper_line = ' /' + "".join(['=' for x in range(len(main)-4)]) + '\\'
            lower_line = ' \\' + "".join(['=' for x in range(len(main)-4)]) + '/'
            cls._log(f'{cls.ANSI.get("bold")}{color}{upper_line}\n{main}\n{lower_line}{default}', )

    @classmethod
    def _get_now(cls, formatting: str = '%H:%M:%S') -> str:
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
    def _get_source(cls, level=2) -> str:
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

            return source if cls.CONFIGS.is_structured or not cls.CONFIGS.source_length else source.ljust(cls.CONFIGS.source_length)[:cls.CONFIGS.source_length]
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
        if cls.CONFIGS.short_source:
            method_module = ".".join([x[:1] for x in method_module.split(".")])
        source = f"{method_module}.{method_class}() <timeit>"
        source = source.ljust(cls.CONFIGS.source_length)[:cls.CONFIGS.source_length] if not cls.CONFIGS.is_structured and cls.CONFIGS.source_length else source
        if not cls.CONFIGS.is_structured:
            cls._log_timeit(f"Elapsed: {elapsed_str}.", source=source)
        else:
            cls._log_timeit(f"Elapsed: {elapsed_str}.", source=source, data={"seconds": round(elapsed_time, 3)})

    @classmethod
    def set_correlation_id(cls, corr_id: str):
        if corr_id is not None and len(corr_id)>0:
            cls.CORRELATION_ID = corr_id
        else:
            cls.CORRELATION_ID = uuid.uuid4()