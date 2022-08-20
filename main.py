import subprocess

from ulauncher.api.client.Extension import Extension
from ulauncher.api.client.EventListener import EventListener
from ulauncher.api.shared.event import KeywordQueryEvent, ItemEnterEvent
from ulauncher.api.shared.item.ExtensionResultItem import ExtensionResultItem
from ulauncher.api.shared.action.ExtensionCustomAction import ExtensionCustomAction
from ulauncher.api.shared.action.RenderResultListAction import RenderResultListAction

from os.path import expanduser

class NeovimSession(Extension):
    def __init__(self):
        super().__init__()
        self.subscribe(KeywordQueryEvent, KeywordQueryEventListener())
        self.subscribe(ItemEnterEvent, ItemEnterEventListener())

    @staticmethod
    def get_preferences(input_preferences):
        preferences = {
            'session_store': expanduser(input_preferences['nvim-session-store']),
            'cmd': input_preferences['nvim-cmd'],
            'fzf': input_preferences['fzf-cmd']
        }
        return preferences

    @staticmethod
    def generate_find_cmd(preferences):
        cmd = ['find', preferences['session_store'], '-maxdepth', '1', '-type', 'f', '-printf', '%f\n']
        return cmd

    def search(self, query, preferences):
        fd_cmd = self.generate_find_cmd(preferences)
        with subprocess.Popen(fd_cmd, stdout=subprocess.PIPE) as fd_proc:
            fzf_cmd = [preferences['fzf'], '--filter', query or '']
            output = subprocess.check_output(fzf_cmd, stdin=fd_proc.stdout, text=True)
            results = output.splitlines()
            return results


class KeywordQueryEventListener(EventListener):

    def on_event(self, event, extension):
        items = []
        preferences = extension.get_preferences(extension.preferences)
        query = event.get_argument()
        results = extension.search(query, preferences)

        def create_result_item(name):
            return ExtensionResultItem(
                icon='images/icon.png',
                name=name,
                on_enter=ExtensionCustomAction({ 'session': name }))

        items = list(map(create_result_item, results))
        return RenderResultListAction(items)

class ItemEnterEventListener(EventListener):
    def on_event(self, event, extension):
        session = event.get_data()['session']
        preferences = extension.get_preferences(extension.preferences)
        cmd = [*preferences['cmd'].split(' '), preferences['session_store'] + '/' + session]
        print(cmd)
        subprocess.Popen(cmd)



if __name__ == '__main__':
    NeovimSession().run()
