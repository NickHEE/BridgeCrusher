def __init__(self):
        super(VideoStyleLight, self).__init__()
        palette = qApp.palette()
        palette.setColor(QPalette.Window, QColor(40, 40, 40))
        palette.setColor(QPalette.WindowText, QColor(230, 230, 230))
        palette.setColor(QPalette.Base, QColor(252, 252, 252))
        palette.setColor(QPalette.AlternateBase, QColor(239, 240, 241))
        palette.setColor(QPalette.ToolTipBase, QColor(239, 240, 241))
        palette.setColor(QPalette.ToolTipText, QColor(49, 54, 59))
        palette.setColor(QPalette.Text, QColor(250, 250, 250))
        palette.setColor(QPalette.Button, QColor(85, 90, 95))
        palette.setColor(QPalette.ButtonText, QColor(210, 210, 210))
        palette.setColor(QPalette.BrightText, QColor(255, 255, 255))
        palette.setColor(QPalette.Link, QColor(41, 128, 185))
        palette.setColor(QPalette.Highlight, QColor(136, 136, 136))
        palette.setColor(QPalette.HighlightedText, QColor(239, 240, 241))
        palette.setColor(QPalette.Disabled, QPalette.Light, Qt.white)
        palette.setColor(QPalette.Disabled, QPalette.Shadow, QColor(234, 234, 234))
        qApp.setPalette(palette) 