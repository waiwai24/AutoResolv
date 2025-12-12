
# This file is part of AutoResolv.
# Copyright 2022 - Airbus, thibault poncetta
# AutoResolv is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation, either version 3 of the License, or (at your
# option) any later version.
# AutoResolv is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
# You should have received a copy of the GNU Affero General Public License
# along with AutoResolv.  If not, see <http://www.gnu.org/licenses/>.

import idaapi
import subprocess
import os
import sys


#class for result print on IDA
class ResultShower(idaapi.Choose):
    def __init__(self, title, items, demangle=False, flags=0, width=None, height=None, embedded=False, modal=False):
        self.demangle = demangle
        if self.demangle:
            idaapi.Choose.__init__(
                self,
                title,
                [
                    ["Function Name", idaapi.Choose.CHCOL_PLAIN|50],
                    ["Library Name", idaapi.Choose.CHCOL_PLAIN|20],
                    ["Path", idaapi.Choose.CHCOL_PLAIN|20],
                    ["C++ Demangled Name", idaapi.Choose.CHCOL_PLAIN|20],

                ],
                flags=flags,
                width=width,
                height=height,
                embedded=embedded)

        else:
            idaapi.Choose.__init__(
                self,
                title,
                [
                    ["Function Name", idaapi.Choose.CHCOL_PLAIN|50],
                    ["Library Name", idaapi.Choose.CHCOL_PLAIN|20],
                    ["Path", idaapi.Choose.CHCOL_PLAIN|20],

                ],
                flags=flags,
                width=width,
                height=height,
                embedded=embedded)


        self.items = items
        self.selcount = 0
        self.n = len(items)
        self.popup_names = ["Open lib in ida"]

    def OnClose(self):
        return
        self.selcount += 1

    def OnSelectLine(self, n):
        pass

    def OnGetLine(self, n):
        res = self.items[n]
        if self.demangle:
            res =   [res[0], res[1], res[2], res[3]]
        else:
            res = [res[0], res[1], res[2]]
        return res

    def OnGetSize(self):
        n = len(self.items)
        return n
    def OnPopup(self, form, popup_handle):
        idaapi.attach_action_to_popup(form, popup_handle, "AutoResolv:OpenLibInIDA", None)
        return True

    def show(self):
        self._register_actions()
        return self.Show() >= 0
    
    def _register_actions(self):

        action_desc = idaapi.action_desc_t(
            "AutoResolv:OpenLibInIDA",
            "Open Library in IDA",
            OpenLibInIDAHandler(self),
            None,
            None,
            0
        )
        
        idaapi.register_action(action_desc)
    
    def _unregister_actions(self):
        idaapi.unregister_action("AutoResolv:OpenLibInIDA")

class OpenLibInIDAHandler(idaapi.action_handler_t):
    
    def __init__(self, result_shower):
        idaapi.action_handler_t.__init__(self)
        self.result_shower = result_shower
    
    def activate(self, ctx):
        selected_index = ctx.chooser_selection[0]
        selected_item = self.result_shower.items[selected_index]
        lib_path = selected_item[2]

        # please configure the IDA executable path in the code        
        ida_path = None  
        
        if ida_path:
            subprocess.Popen([ida_path, lib_path])
            print(f"[AutoResolv] Successfully launched IDA to analyze library file: {lib_path}")
        else:
            print("[AutoResolv] Please configure the IDA executable path in the code, or manually open the library file")
        return 1
    
    def update(self, ctx):
        return idaapi.AST_ENABLE_ALWAYS
