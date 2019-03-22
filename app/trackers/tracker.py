import pyHook

class Tracker(object):

    instances = []
    pyhook_manager = None

    def __new__(cls, *args, **kwargs):
        instance = object.__new__(cls, *args, **kwargs)
        cls.instances.append(instance)
        return instance

    @classmethod
    def initialize(cls):
        cls.pyhook_manager.HookKeyboard()
        for inst in cls.instances:
            inst.init_hook()

    @classmethod
    def uninitialize(cls):
        cls.pyhook_manager.UnhookKeyboard()
        for inst in cls.instances:
            inst.uninit_hook()

    @classmethod
    def gen_run(cls, delta):
        for inst in cls.instances:
            inst.run(delta)

    @classmethod
    def gen_key_handler(cls, event):
        for inst in cls.instances:
            inst.key_handler(event)
        return True

    def key_handler(self, event):
        raise NotImplementedError

    def init_hook(self):
        pass

    def uninit_hook(self):
        pass

    def run(self, delta):
        raise NotImplementedError

Tracker.pyhook_manager = pyHook.HookManager()