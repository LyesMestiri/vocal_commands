from PyQt5 import QtGui as qtg
from PyQt5 import QtWidgets as qtw
from PyQt5 import QtCore as qtc
from PyQt5 import QtMultimedia as qtmm

from os import mkfifo, unlink
import random
import time

from analyzer import Analyzer

IMG_BOMB = qtg.QImage("./images/bug.png")
IMG_FLAG = qtg.QImage("./images/flag.png")
IMG_START = qtg.QImage("./images/rocket.png")
IMG_CLOCK = qtg.QImage("./images/clock-select.png")
IMG_TIME = qtg.QImage("./images/hourglass.png")

NUM_COLORS = {
    1: qtg.QColor('#f44336'),
    2: qtg.QColor('#9C27B0'),
    3: qtg.QColor('#3F51B5'),
    4: qtg.QColor('#03A9F4'),
    5: qtg.QColor('#00BCD4'),
    6: qtg.QColor('#4CAF50'),
    7: qtg.QColor('#E91E63'),
    8: qtg.QColor('#FF9800')
}

LEVELS = [
    (8, 10),
    (16, 40),
    (24, 99)
]

STATUS_READY = 0
STATUS_PLAYING = 1
STATUS_FAILED = 2
STATUS_SUCCESS = 3
STATUS_PAUSED = 4

STATUS_ICONS = {
    STATUS_READY: "./images/plus.png",
    STATUS_PLAYING: "./images/smiley.png",
    STATUS_FAILED: "./images/cross.png",
    STATUS_SUCCESS: "./images/smiley-lol.png",
    STATUS_PAUSED: "./images/hourglass.png",
}

    

class Pos(qtw.QWidget):
    expandable = qtc.pyqtSignal(int, int)
    clicked = qtc.pyqtSignal()
    ohno = qtc.pyqtSignal()

    def __init__(self, x, y, mainWindow, *args, **kwargs):
        super(Pos, self).__init__(*args, **kwargs)

        self.setFixedSize(qtc.QSize(20, 20))
        self.mainWindow = mainWindow

        self.x = x
        self.y = y

    def reset(self):
        self.is_start = False
        self.is_mine = False
        self.adjacent_n = 0

        self.is_revealed = False
        self.is_flagged = False
        
        self.is_selected = False

        self.update()

    def paintEvent(self, event):
        p = qtg.QPainter(self)
        p.setRenderHint(qtg.QPainter.Antialiasing)

        r = event.rect()

        if self.is_revealed:
            color = self.palette().color(qtg.QPalette.Background)
            outer, inner = color, color
        else:
            outer, inner = qtc.Qt.gray, qtc.Qt.lightGray

        p.fillRect(r, qtg.QBrush(inner))
        pen = qtg.QPen(outer)
        pen.setWidth(1)
        p.setPen(pen)
        p.drawRect(r)
        
        if self.is_selected and self.mainWindow.status in (STATUS_PLAYING, STATUS_READY):
            pen = qtg.QPen(NUM_COLORS[1])
            pen.setWidth(3)
            p.setPen(pen)
            p.drawRect(0, 0, 20, 20)

        if self.is_revealed:
            if self.is_start:
                p.drawPixmap(r, qtg.QPixmap(IMG_START))

            elif self.is_mine:
                p.drawPixmap(r, qtg.QPixmap(IMG_BOMB))

            elif self.adjacent_n > 0:
                pen = qtg.QPen(NUM_COLORS[self.adjacent_n])
                p.setPen(pen)
                f = p.font()
                f.setBold(True)
                p.setFont(f)
                p.drawText(r, qtc.Qt.AlignHCenter | qtc.Qt.AlignVCenter, str(self.adjacent_n))

        elif self.is_flagged:
            p.drawPixmap(r, qtg.QPixmap(IMG_FLAG))

    def flag(self):
        self.is_flagged = True
        self.update()

        self.clicked.emit()

    def reveal(self):
        self.is_revealed = True
        self.update()

    def click(self):
        if not self.is_revealed:
            self.reveal()
            if self.adjacent_n == 0:
                self.expandable.emit(self.x, self.y)

        self.clicked.emit()
        
        if self.is_mine:
            self.ohno.emit()
    
    
    def mouseReleaseEvent(self, e):
        if e.button() == qtc.Qt.RightButton and not self.is_revealed:
            self.flag()
        
        elif e.button() == qtc.Qt.LeftButton:
            self.click()
        

class MainWindow(qtw.QMainWindow):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        self.x = 0
        self.y = 0
        self.speed = 0

        self.b_size, self.n_mines = LEVELS[1]

        w = qtw.QWidget()
        hb = qtw.QHBoxLayout()

        self.mines = qtw.QLabel()
        self.mines.setAlignment(qtc.Qt.AlignHCenter | qtc.Qt.AlignVCenter)

        self.clock = qtw.QLabel()
        self.clock.setAlignment(qtc.Qt.AlignHCenter | qtc.Qt.AlignVCenter)

        f = self.mines.font()
        f.setPointSize(24)
        f.setWeight(75)
        self.mines.setFont(f)
        self.clock.setFont(f)

        self._timer = qtc.QTimer()
        self._timer.timeout.connect(self.update_timer)
        self._timer.start(1000)  # 1 second timer

        self.mines.setText("%03d" % self.n_mines)
        self.clock.setText("000")

        self.button = qtw.QPushButton()
        self.button.setFixedSize(qtc.QSize(32, 32))
        self.button.setIconSize(qtc.QSize(32, 32))
        self.button.setIcon(qtg.QIcon("./images/smiley.png"))
        self.button.setFlat(True)

        self.button.pressed.connect(self.on)

        l = qtw.QLabel()
        l.setPixmap(qtg.QPixmap.fromImage(IMG_BOMB))
        l.setAlignment(qtc.Qt.AlignRight | qtc.Qt.AlignVCenter)
        hb.addWidget(l)

        hb.addWidget(self.mines)
        hb.addWidget(self.button)
        hb.addWidget(self.clock)

        l = qtw.QLabel()
        l.setPixmap(qtg.QPixmap.fromImage(IMG_CLOCK))
        l.setAlignment(qtc.Qt.AlignLeft | qtc.Qt.AlignVCenter)
        hb.addWidget(l)

        vb = qtw.QVBoxLayout()
        vb.addLayout(hb)

        self.grid = qtw.QGridLayout()
        self.grid.setSpacing(5)

        vb.addLayout(self.grid)
        w.setLayout(vb)
        self.setCentralWidget(w)

        self.init_map()
        self.update_status(STATUS_READY)

        self.reset_map()
        self.update_status(STATUS_READY)
        
        #NOUVEAU : Recorder
        self.recorder = qtmm.QAudioRecorder()
    
        self.recorder.setAudioInput('default:') #NO EXCEPTION ! -> write right input
        sample_path = qtc.QDir.home().filePath('Documents/Cours/ING3/Projet/vocalCommand/vocal_commands/minesweeper/enregistrements/enr.wav')#'./enregistrements/enr.wav'
        try :
            unlink(sample_path)
        except:
            pass
        mkfifo(sample_path)
        self.recorder.setOutputLocation(qtc.QUrl.fromLocalFile(sample_path))
        self.recorder.setContainerFormat('audio/x-wav')

        self.analyzer = Analyzer()
        self.analyzer.start()

        self.timer = qtc.QTimer(self)
        self.timer.setInterval(10)
        self.timer.timeout.connect(self.get_network_results)

        self.show()
        self.timer.start()
        self.recorder.record()

    def get_network_results(self):
        resp = self.analyzer.read_response()

        if resp is None:
            return
        cmd = resp[0]

        self.assign(cmd)

    def init_map(self):
        # Add positions to the map
        for x in range(0, self.b_size):
            for y in range(0, self.b_size):
                w = Pos(x, y, self)
                self.grid.addWidget(w, y, x)
                # Connect signal to handle expansion.
                w.clicked.connect(self.trigger_start)
                w.expandable.connect(self.expand_reveal)
                w.ohno.connect(self.game_over)

    def reset_map(self):
        # Clear all mine positions
        for x in range(0, self.b_size):
            for y in range(0, self.b_size):
                w = self.grid.itemAtPosition(y, x).widget()
                w.reset()

        # Add mines to the positions
        positions = []
        while len(positions) < self.n_mines:
            x, y = random.randint(0, self.b_size - 1), random.randint(0, self.b_size - 1)
            if (x, y) not in positions:
                w = self.grid.itemAtPosition(y, x).widget()
                w.is_mine = True
                positions.append((x, y))

        def get_adjacency_n(x, y):
            positions = self.get_surrounding(x, y)
            n_mines = sum(1 if w.is_mine else 0 for w in positions)

            return n_mines

        # Add adjacencies to the positions
        for x in range(0, self.b_size):
            for y in range(0, self.b_size):
                w = self.grid.itemAtPosition(y, x).widget()
                w.adjacent_n = get_adjacency_n(x, y)

        # Place starting marker
        while True:
            x, y = random.randint(0, self.b_size - 1), random.randint(0, self.b_size - 1)
            w = self.grid.itemAtPosition(y, x).widget()
            # We don't want to start on a mine.
            if (x, y) not in positions:
                w = self.grid.itemAtPosition(y, x).widget()
                w.is_start = True
                w.is_selected = True
                self.x, self.y = x, y

                # Reveal all positions around this, if they are not mines either.
                for w in self.get_surrounding(x, y):
                    if not w.is_mine:
                        w.click()
                break

    def get_surrounding(self, x, y):
        positions = []

        for xi in range(max(0, x - 1), min(x + 2, self.b_size)):
            for yi in range(max(0, y - 1), min(y + 2, self.b_size)):
                positions.append(self.grid.itemAtPosition(yi, xi).widget())

        return positions

    def reveal_map(self):
        for x in range(0, self.b_size):
            for y in range(0, self.b_size):
                w = self.grid.itemAtPosition(y, x).widget()
                w.reveal()

    def expand_reveal(self, x, y):
        for xi in range(max(0, x - 1), min(x + 2, self.b_size)):
            for yi in range(max(0, y - 1), min(y + 2, self.b_size)):
                w = self.grid.itemAtPosition(yi, xi).widget()
                if not w.is_mine:
                    w.click()

    def trigger_start(self, *args):
        if self.status == STATUS_READY:
            # First click.
            self.update_status(STATUS_PLAYING)
            # Start timer.
            self._timer_start_nsecs = int(time.time())

    def update_status(self, status):
        self.status = status
        self.button.setIcon(qtg.QIcon(STATUS_ICONS[self.status]))

    def update_timer(self):
        if self.status == STATUS_PLAYING:
            n_secs = int(time.time()) - self._timer_start_nsecs
            self.clock.setText("%03d" % n_secs)
        elif self.status == STATUS_PAUSED:
            self._timer_start_nsecs += 1
            
    def game_over(self):
        self.reveal_map()
        self.update_status(STATUS_FAILED)
        
    def assign(self, command):
        print(command)
        commands = {
            'yes': self.front, 'no': self.back, 'go':self.click, 'start':self.start, 'stop': self.flag,
            'right':self.right, 'left':self.left, 'up':self.up, 'down':self.down, 'on':self.on, 'off':self.off,
            'unknown':self.unknown
        }
        commands[command]()
        self.update()

    def click(self):
        self.grid.itemAtPosition(self.y, self.x).widget().click()

    def right(self) :
        self.speed = 1
        self.grid.itemAtPosition(self.y, self.x).widget().is_selected = False
        self.x = (self.x + 1)%self.b_size
        self.grid.itemAtPosition(self.y, self.x).widget().is_selected = True
        
    def left(self) :
        self.speed = 2
        self.grid.itemAtPosition(self.y, self.x).widget().is_selected = False
        self.x = (self.x - 1)%self.b_size
        self.grid.itemAtPosition(self.y, self.x).widget().is_selected = True
        
    def up(self) :
        self.speed = 3
        self.grid.itemAtPosition(self.y, self.x).widget().is_selected = False
        self.y = (self.y - 1)%self.b_size
        self.grid.itemAtPosition(self.y, self.x).widget().is_selected = True
        
    def down(self) :
        self.speed = 0
        self.grid.itemAtPosition(self.y, self.x).widget().is_selected = False
        self.y = (self.y + 1)%self.b_size
        self.grid.itemAtPosition(self.y, self.x).widget().is_selected = True
        
    def flag(self) :
        self.grid.itemAtPosition(self.y, self.x).widget().flag()

    def front(self) :
        if self.speed == 0 : #down
            self.grid.itemAtPosition(self.y, self.x).widget().is_selected = False
            self.y = self.b_size-1
            self.grid.itemAtPosition(self.y, self.x).widget().is_selected = True
        elif self.speed == 1 : #right
            self.grid.itemAtPosition(self.y, self.x).widget().is_selected = False
            self.x = self.b_size-1
            self.grid.itemAtPosition(self.y, self.x).widget().is_selected = True
        elif self.speed == 2 : #left
            self.grid.itemAtPosition(self.y, self.x).widget().is_selected = False
            self.y = 0
            self.grid.itemAtPosition(self.y, self.x).widget().is_selected = True
        elif self.speed == 3 : #up
            self.grid.itemAtPosition(self.y, self.x).widget().is_selected = False
            self.x = 0
            self.grid.itemAtPosition(self.y, self.x).widget().is_selected = True

    def back(self) :
        if self.speed == 0 : #down
            self.grid.itemAtPosition(self.y, self.x).widget().is_selected = False
            self.y = 0
            self.grid.itemAtPosition(self.y, self.x).widget().is_selected = True
        elif self.speed == 1 : #right
            self.grid.itemAtPosition(self.y, self.x).widget().is_selected = False
            self.x = 0
            self.grid.itemAtPosition(self.y, self.x).widget().is_selected = True
        elif self.speed == 2 : #left
            self.grid.itemAtPosition(self.y, self.x).widget().is_selected = False
            self.y = self.b_size-1
            self.grid.itemAtPosition(self.y, self.x).widget().is_selected = True
        elif self.speed == 3 : #up
            self.grid.itemAtPosition(self.y, self.x).widget().is_selected = False
            self.x = self.b_size-1
            self.grid.itemAtPosition(self.y, self.x).widget().is_selected = True

    def on(self) :
        if self.status == STATUS_FAILED:
            self.update_status(STATUS_READY)
            self.reset_map()   
        else :
            print('Status On Error')
            print('Trying to turn on while status:', self.status)   
            
    def off(self) :
        if self.status == STATUS_PLAYING:
            self.update_status(STATUS_FAILED)
            self.reveal_map()
        else :
            print('Status Off Error')   
            
    def start(self):
        if self.status == STATUS_PLAYING :
            self.status = STATUS_PAUSED
        elif self.status == STATUS_PAUSED :
            self.status = STATUS_PLAYING
            
    def unknown(self) :
        pass

    def closeEvent(self, close_ev):
        super().closeEvent(close_ev)

if __name__ == '__main__':
    app = qtw.QApplication([])
    window = MainWindow()
    # analyse(window)
    app.exec_()