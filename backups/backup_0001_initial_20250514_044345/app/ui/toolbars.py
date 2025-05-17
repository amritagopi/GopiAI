# ui/toolbars.py
from app.ui.i18n.translator import tr

def create_toolbars(main_window):
    """Создает панели инструментов."""
    main_window.main_toolbar = main_window.addToolBar(tr("toolbar.main", "Main Toolbar"))
    main_window.main_toolbar.setObjectName("MainToolBar")
    main_window.main_toolbar.setMovable(True)

    if hasattr(main_window, "new_file_action"):
        main_window.main_toolbar.addAction(main_window.new_file_action)
    if hasattr(main_window, "open_file_action"):
        main_window.main_toolbar.addAction(main_window.open_file_action)
    if hasattr(main_window, "save_file_action"):
        main_window.main_toolbar.addAction(main_window.save_file_action)

    main_window.main_toolbar.addSeparator()

    if hasattr(main_window, "cut_action"):
        main_window.main_toolbar.addAction(main_window.cut_action)
    if hasattr(main_window, "copy_action"):
        main_window.main_toolbar.addAction(main_window.copy_action)
    if hasattr(main_window, "paste_action"):
        main_window.main_toolbar.addAction(main_window.paste_action)

    main_window.main_toolbar.addSeparator()

    if hasattr(main_window, "undo_action"):
        main_window.main_toolbar.addAction(main_window.undo_action)
    if hasattr(main_window, "redo_action"):
        main_window.main_toolbar.addAction(main_window.redo_action)
