import traceback

import json, inspect
import os, textwrap, time, platform, threading
import uuid
from datetime import datetime


class StructuredLog:

    def __init__(self,
                 level: str,
                 source: str,
                 message: str,
                 data,
                 corr_id: str,
                 customer_name: str):
        self.lvl = level
        self.msg = message
        self.src = source
        self.data = data
        self.timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]
        self.corr_id = corr_id
        self.customer_name = customer_name

class AppLogger:
    """
    Test logger object class. Formats, prints, and saves messages to local logs folder.
    """

    LOG_SAVE_PATH = 'logs'                          # :str: Default log saving location.
    HEADER_SIZE = 80                                # :int: Length of the headers.
    WRAPPER = textwrap.TextWrapper(width=20000)     # :TextWrapper: Maximum amount of characters per line.
    MAXIMUM_LOG_FILES_STORED = 5                    # :int: Maximum amount of stored log files.
    LOG_STORAGE = []                                # :list: Logs memory storage.
    MEASUREMENT_STORAGE = []                        # :list: Measurements memory storage.
    # TIMEZONE = 'UTC'
    STRUCTURED = True
    SHORT_SOURCE = True
    TIMEZONE = ''
    ANSI = {                                        # :dict: ANSI decorations for terminal.
        'magenta': '\u001b[35m',
        'yellow': '\u001b[33m',
        'red': '\u001b[31m',
        'green': '\u001b[32m',
        'bg_green': '\u001b[42m',
        'bg_red': '\u001b[41m',
        'bold': '\u001b[1m',
        'underline': '\u001b[4m',
        'reversed': '\u001b[7m',
        'default': '\u001b[0m'
    }

    CORRELATION_ID = None
    CUSTOMER_NAME = None

    @classmethod
    def highlight(cls, msg: str, print_on_screen: bool = True, say = False, data = None):
        """
        Logs default alert message.
        :param msg: Message to be logged.
        :param print_on_screen: Flags whether message is to be printed on screen or only on file.
        :return: void
        """

        if not cls.STRUCTURED:
            magenta, reverse, default = cls.ANSI.get('magenta'), cls.ANSI.get('reversed'), cls.ANSI.get('default')
            msg = f"{magenta}{reverse}{cls.__get_now('%H:%M:%S')}{default}{magenta} {magenta}{reverse}{cls.get_source()}{default}{magenta} {msg}{default}"
            cls.log(msg, print_on_screen=print_on_screen, data=data)
            if say:
                cls.__say(f'{msg}')
        else:
            cls.log(msg, level="INFO", print_on_screen=print_on_screen, data=data)

    @classmethod
    def info(cls, msg: str, print_on_screen: bool = True, say = False, data = None):
        """
        Logs default alert message.
        :param msg: Message to be logged.
        :param print_on_screen: Flags whether message is to be printed on screen or only on file.
        :return: void
        """

        if not cls.STRUCTURED:
            reverse, default = cls.ANSI.get('reversed'), cls.ANSI.get('default')
            msg_ansi = f"{reverse}{cls.__get_now('%H:%M:%S')}{default} {reverse}{cls.get_source()}{default} {msg}"
            cls.log(msg_ansi, print_on_screen=print_on_screen, data=data)
            if say:
                cls.__say(f'{msg}')
        else:
            cls.log(msg, level="INFO", print_on_screen=print_on_screen, data=data)

    @classmethod
    def warn(cls, msg: str, print_on_screen: bool = True, say = False, data = None):
        """
        Logs default alert message.
        :param msg: Message to be logged.
        :param print_on_screen: Flags whether message is to be printed on screen or only on file.
        :return: void
        """

        if not cls.STRUCTURED:
            yellow, reverse, default = cls.ANSI.get('yellow'), cls.ANSI.get('reversed'), cls.ANSI.get('default')
            msg_ansi = f"{yellow}{reverse}{cls.__get_now('%H:%M:%S')}{default} {yellow}{reverse}{cls.get_source()}{default} {yellow}{msg}{default}"
            cls.log(msg_ansi, print_on_screen=print_on_screen, data=data)
            if say:
                cls.__say(f'Alert. {msg}')
        else:
            cls.log(msg, level="WARN", print_on_screen=print_on_screen, data=data)

    @classmethod
    def error(cls, msg: str, exception: Exception = None, print_on_screen: bool = True, say = False, data = None):
        """
        Logs default error message.
        :param msg: Message to be logged.
        :param print_on_screen: Flags whether message is to be printed on screen of only on file.
        :return: void
        """

        if not cls.STRUCTURED:
            red, reverse, default = cls.ANSI.get('red'), cls.ANSI.get('reversed'), cls.ANSI.get('default')
            msg_ansi = f"{red}{reverse}{cls.__get_now('%H:%M:%S')}{default} {red}{reverse}{cls.get_source()}{default} {red}{msg}{default}"

            if exception:
                msg_ansi += f"\n{red}"
                msg_ansi += "\n".join(traceback.format_exception(type(exception), exception, exception.__traceback__))
                msg_ansi += f"{default}"

            cls.log(msg_ansi, print_on_screen=print_on_screen, data=data)

            if say:
                cls.__say(f'Error. {msg}')
        else:
            cls.log(msg, level="ERROR", print_on_screen=print_on_screen, data=data)
            if exception:
                stack_trace = "".join(traceback.format_exception(type(exception), exception, exception.__traceback__))
                cls.log(stack_trace, print_on_screen=print_on_screen)

    @classmethod
    def log_timeit(cls, msg: str, print_on_screen: bool = True, data=None, source=None):
        """
        Logs default alert message.
        :param msg: Message to be logged.
        :param print_on_screen: Flags whether message is to be printed on screen or only on file.
        :return: void
        """

        if not cls.STRUCTURED:
            yellow, reverse, default = cls.ANSI.get('yellow'), cls.ANSI.get('reversed'), cls.ANSI.get('default')
            msg_ansi = f"{yellow}{reverse}{cls.__get_now('%H:%M:%S')}{default} {yellow}{reverse} {source} {default} {yellow}{msg}{default}"
            cls.log(msg_ansi, print_on_screen=print_on_screen)
        else:
            cls.log(msg, level="INFO", print_on_screen=print_on_screen, data=data, source=source)

    @classmethod
    def empty_line(cls):
        if not cls.STRUCTURED:
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

        if ignore_wrap:
            if print_on_screen: cls.log_structured(line, level, data, source)
            cls.LOG_STORAGE.append(line)
        else:
            wrap_list = cls.WRAPPER.wrap(text=line)
            for wrap_line in wrap_list:
                if print_on_screen: cls.log_structured(wrap_line, level, data, source)
                cls.LOG_STORAGE.append(wrap_line)

    @classmethod
    def log_structured(cls, line, level, data=None, source=None):
        if not cls.STRUCTURED:
            print(line)
            if data is None: return
            if isinstance(data, str):
                print(data)
            else:
                print(json.dumps(data, indent=4, default=str, ensure_ascii=False))
        else:
            log = StructuredLog(
                level=level,
                source=cls.get_source(4) if source is None else source,
                message=line,
                data=data,
                corr_id=cls.CORRELATION_ID,
                customer_name=cls.CUSTOMER_NAME
            )
            print(json.dumps(log.__dict__, default=str, ensure_ascii=False))

    @classmethod
    def save_logs(cls):
        """
        Saves acquired log lines to .txt file at default log file location with auto generated name.
        :return: void.
        """

        # Removes oldest log file if maximum threshold has been reached.
        path = cls.LOG_SAVE_PATH
        log_files = [f"{path}/{name}" for name in os.listdir(path) if os.path.isfile(os.path.join(path, name))]
        no_of_logs = len(log_files)
        if no_of_logs >= cls.MAXIMUM_LOG_FILES_STORED:
            oldest_file = min(log_files, key=os.path.getctime)
            os.remove(oldest_file)

        # Saves current log lines in new log file.
        log_path_and_name = f'{path}/{datetime.now().strftime("%Y-%m-%d_%H-%M-%S")}.txt'
        strings_to_replace = [v for k, v in cls.ANSI.items()]
        with open(log_path_and_name, "w") as txt_file:
            for line in cls.LOG_STORAGE:
                for reps in strings_to_replace:
                    line = line.replace(reps, '')
                txt_file.write(''.join(line) + '\n')

    @classmethod
    def print_header(cls, content):
        """
        Prints main header on log screen.
        :param content (string): Text to be displayed on main header.
        :return: void
        """

        if not cls.STRUCTURED:
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
            stack = inspect.stack()
            locals_key = "self" if "self" in stack[level][0].f_locals.keys() else "cls"
            the_module = stack[level][0].f_locals[locals_key].__class__.__module__
            the_class = stack[level][0].f_locals[locals_key].__class__.__name__
            the_method = stack[level][0].f_code.co_name
            if cls.SHORT_SOURCE:
                the_module = ".".join([x[:1] for x in the_module.split(".")])
            result = "{}.{}.{}()".format(the_module, the_class, the_method)
            if not cls.STRUCTURED:
                result = f" {result} "
            return result
        except Exception as e:
            if not cls.STRUCTURED:
                return " N.A. "
            else:
                return "N.A."

    @classmethod
    def get_measurements(cls):
        return cls.MEASUREMENT_STORAGE

    @classmethod
    def get_measurements_avg(cls):
        if len(cls.MEASUREMENT_STORAGE) == 0: return 0
        return sum([x['duration'] for x in cls.MEASUREMENT_STORAGE])/len(cls.MEASUREMENT_STORAGE)

    @classmethod
    def get_measurements_highest(cls, no_of_measurements):
        no_of_measurements = min(no_of_measurements, len(cls.MEASUREMENT_STORAGE))
        return sorted(cls.MEASUREMENT_STORAGE, key=lambda x: x['duration'], reverse=True)[:no_of_measurements]

    @classmethod
    def get_measurements_lowest(cls, no_of_measurements):
        no_of_measurements = min(no_of_measurements, len(cls.MEASUREMENT_STORAGE))
        return sorted(cls.MEASUREMENT_STORAGE, key=lambda x: x['duration'], reverse=False)[:no_of_measurements]

    @classmethod
    def timeit(cls):
        """
        Decorator to log current function execution time.
        :param name: Procedure name to be displayed.
        :return: void.
        """

        def decorator(method):
            def measure(*args, **kw):
                ts = time.time()
                result = method(*args, **kw)
                te = time.time()
                tf = te - ts
                tf_str = ''
                if tf < 60:
                    tf_str = str(round(tf, 3)) + 's'
                else:
                    seconds = tf % 60
                    tf_str = f"{int(tf // 60)}m{' ' + str(round(seconds, 3)) + 's' if seconds > 0 else '' }"
                method_module = inspect.getmodule(method).__name__
                method_class = method.__qualname__
                if not cls.STRUCTURED and cls.SHORT_SOURCE:
                    method_module = ".".join([x[:1] for x in method_module.split(".")])
                source = "{}.{}()".format(method_module, method_class)
                if not cls.STRUCTURED:
                    cls.log_timeit(f"Elapsed: {tf_str}", source=source)
                else:
                    cls.log_timeit(f"Elapsed: {tf_str}", source=source, data={"seconds": round(tf, 3)})
                cls.MEASUREMENT_STORAGE.append({
                    'time': cls.__get_now('%H:%M:%S'),
                    'duration': tf
                })
                return result
            return measure
        return decorator

    @classmethod
    def set_correlation_id(cls, corr_id: str):
        if corr_id is not None and len(corr_id)>0:
            cls.CORRELATION_ID = corr_id
        else:
            cls.CORRELATION_ID = uuid.uuid4()

    @classmethod
    def set_customer_name(cls, customer_name: str):
        cls.CUSTOMER_NAME = customer_name