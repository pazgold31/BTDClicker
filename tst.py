import PySimpleGUI as sg

data = [f'Item {i + 1:0>2d}' for i in range(10)]

layout = [
    [sg.Listbox(
        values=data,
        select_mode=sg.LISTBOX_SELECT_MODE_EXTENDED,
        size=(20, 5),
        enable_events=True,
        key="-LISTBOX-",
        metadata=[],
    )],
]
window = sg.Window('Listbox', layout, finalize=True)
listbox = window["-LISTBOX-"]

while True:

    event, values = window.read()

    if event == sg.WINDOW_CLOSED:
        break
    print(event, values)
    if event == "-LISTBOX-":
        metadata = listbox.metadata
        selections = values["-LISTBOX-"]
        print(metadata, selections)
        if metadata == selections:
            listbox.update(set_to_index=[])
            listbox.metadata = []
        else:
            listbox.metadata = values["-LISTBOX-"]

window.close()
