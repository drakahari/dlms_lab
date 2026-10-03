"""Native entry point: python3 -m learning_lab."""
import argparse
import sys
from pathlib import Path
from PySide6.QtCore import QUrl, QStandardPaths, QLockFile
from PySide6.QtGui import QGuiApplication
from PySide6.QtQml import QQmlApplicationEngine
from PySide6.QtQuickControls2 import QQuickStyle


def load_bundled_scenarios():
    """Existing catalog plus in-memory identity for the checkpoint 1 adapter."""
    from .domain.engine import load_catalog
    from .legacy_scenario import adapt_gateway_dns
    raw = [(Path(__file__).parent / 'packs' / name).read_bytes()
           for name in ('gateway-dns.json', 'subnet-boundary.json', 'service-firewall.json')]
    gateway = adapt_gateway_dns(raw[0])
    packs = load_catalog(raw)
    packs[0] = gateway.legacy_pack()
    return packs, gateway


class ProfileLocks:
    """One lifecycle handle for both authoritative profile roots."""
    def __init__(self, data_root, config_root):
        self.locks = []
        try:
            for root in dict.fromkeys((data_root.resolve(), config_root.resolve())):
                lock = QLockFile(str(root / 'writer.lock'))
                lock.setStaleLockTime(0)
                if not lock.tryLock(0):
                    raise RuntimeError('Learning Lab is already using this data or settings directory. Close its other window first.')
                self.locks.append(lock)
            if len(self.locks) == 1: self.locks.append(self.locks[0])
        except Exception:
            self.unlock()
            raise

    def isLocked(self): return bool(self.locks) and all(lock.isLocked() for lock in self.locks)

    def unlock(self):
        for lock in self.locks: lock.unlock()


def build_application(data_root=None, config_root=None):
    from .catalog import CatalogBridge
    app = QGuiApplication.instance() or QGuiApplication(sys.argv)
    app.setApplicationName('omarchy-learning-lab')
    app.setApplicationDisplayName('Omarchy Learning Lab')
    app.setDesktopFileName('omarchy-learning-lab')
    QQuickStyle.setStyle('Basic')
    data_root = Path(data_root or QStandardPaths.writableLocation(QStandardPaths.AppDataLocation))
    config_root = Path(config_root or QStandardPaths.writableLocation(QStandardPaths.AppConfigLocation))
    data_root.mkdir(parents=True, exist_ok=True)
    config_root.mkdir(parents=True, exist_ok=True)
    lock = ProfileLocks(data_root, config_root)
    packs, gateway = load_bundled_scenarios()
    bridge = CatalogBridge(packs, data_root, config_root)
    bridge.profile_locks = lock
    # Runtime identity is deliberately outside pack dictionaries and records.
    bridge.gateway_scenario = gateway
    engine = QQmlApplicationEngine()
    engine.setInitialProperties({'controller': bridge})
    engine.load(QUrl.fromLocalFile(str(Path(__file__).parent / 'qml/Main.qml')))
    if not engine.rootObjects():
        raise RuntimeError('Could not load the native QML window.')
    app.aboutToQuit.connect(bridge.flush)
    return app, engine, bridge, lock

def main():
    parser = argparse.ArgumentParser(description='Offline native learning lab')
    parser.add_argument('--data-dir', type=Path, help='Isolated data directory for acceptance tests')
    parser.add_argument('--config-dir', type=Path, help='Isolated preferences directory for acceptance tests')
    args = parser.parse_args()
    try:
        app, engine, bridge, lock = build_application(args.data_dir, args.config_dir)
    except (OSError, ValueError, RuntimeError) as exc:
        print(f'Learning Lab: {exc}', file=sys.stderr)
        return 1
    return app.exec()

if __name__ == '__main__':
    raise SystemExit(main())
