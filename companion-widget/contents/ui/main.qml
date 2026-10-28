import QtQuick
import QtQuick.Layouts
import org.kde.plasma.plasmoid

PlasmoidItem {
    width: 620
    height: 690
    Layout.minimumWidth: 390
    Layout.minimumHeight: 520
    preferredRepresentation: fullRepresentation
    Plasmoid.backgroundHints: "NoBackground"
    fullRepresentation: CalendarView { }
}
