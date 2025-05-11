# ui/status_bar.py
from PySide6.QtWidgets import QLabel, QProgressBar
from app.ui.i18n.translator import tr

def create_status_bar(main_window):
    """Создает и настраивает статус-бар."""
    main_window.status_bar = main_window.statusBar()
    main_window.status_bar.setSizeGripEnabled(True)

    main_window.status_label = QLabel(tr("status.ready", "Ready"))
    main_window.status_bar.addPermanentWidget(main_window.status_label, 1)

    main_window.file_info_label = QLabel("")
    main_window.status_bar.addPermanentWidget(main_window.file_info_label)

    main_window.agent_status_label = QLabel("")
    main_window.status_bar.addPermanentWidget(main_window.agent_status_label)

    main_window.progress_bar = QProgressBar()
    main_window.progress_bar.setMaximumWidth(150)
    main_window.progress_bar.setMaximumHeight(15)
    main_window.progress_bar.setVisible(False)
    main_window.status_bar.addPermanentWidget(main_window.progress_bar)
