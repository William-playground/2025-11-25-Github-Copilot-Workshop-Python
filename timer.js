/**
 * ポモドーロタイマー - JavaScript実装
 * カウントダウンタイマー、円グラフの動的描画、開始・リセット機能
 */

class PomodoroTimer {
    constructor() {
        // タイマー設定（25分）
        this.defaultMinutes = 25;
        this.totalSeconds = this.defaultMinutes * 60;
        this.remainingSeconds = this.totalSeconds;
        this.isRunning = false;
        this.intervalId = null;
        
        // 進捗トラッキング
        this.completedPomodoros = 0;
        this.totalFocusMinutes = 0;
        
        // DOM要素の取得
        this.minutesDisplay = document.getElementById('minutes');
        this.secondsDisplay = document.getElementById('seconds');
        this.startBtn = document.getElementById('startBtn');
        this.resetBtn = document.getElementById('resetBtn');
        this.progressCircle = document.querySelector('.timer-progress');
        this.completedCountDisplay = document.getElementById('completedCount');
        this.totalTimeDisplay = document.getElementById('totalTime');
        
        // 円周の計算（2 * π * r）
        this.circumference = 2 * Math.PI * 90;
        
        // 初期化
        this.init();
    }
    
    /**
     * 初期化処理
     */
    init() {
        // 円グラフの初期設定
        this.progressCircle.style.strokeDasharray = this.circumference;
        this.progressCircle.style.strokeDashoffset = 0;
        
        // イベントリスナーの設定
        this.startBtn.addEventListener('click', () => this.toggleTimer());
        this.resetBtn.addEventListener('click', () => this.resetTimer());
        
        // 初期表示の更新
        this.updateDisplay();
        this.updateProgress();
    }
    
    /**
     * タイマーの開始/停止を切り替える
     */
    toggleTimer() {
        if (this.isRunning) {
            this.pauseTimer();
        } else {
            this.startTimer();
        }
    }
    
    /**
     * タイマーを開始する
     */
    startTimer() {
        this.isRunning = true;
        this.startBtn.textContent = '停止';
        this.startBtn.classList.add('running');
        
        this.intervalId = setInterval(() => {
            if (this.remainingSeconds > 0) {
                this.remainingSeconds--;
                this.updateDisplay();
                this.updateProgress();
            } else {
                this.completePomodoro();
            }
        }, 1000);
    }
    
    /**
     * タイマーを一時停止する
     */
    pauseTimer() {
        this.isRunning = false;
        this.startBtn.textContent = '開始';
        this.startBtn.classList.remove('running');
        
        if (this.intervalId) {
            clearInterval(this.intervalId);
            this.intervalId = null;
        }
    }
    
    /**
     * タイマーをリセットする
     */
    resetTimer() {
        this.pauseTimer();
        this.remainingSeconds = this.totalSeconds;
        this.updateDisplay();
        this.updateProgress();
    }
    
    /**
     * ポモドーロ完了時の処理
     */
    completePomodoro() {
        this.pauseTimer();
        this.completedPomodoros++;
        this.totalFocusMinutes += this.defaultMinutes;
        this.updateStats();
        this.remainingSeconds = this.totalSeconds;
        this.updateDisplay();
        this.updateProgress();
        
        // 完了通知（ブラウザ対応時）
        if (Notification.permission === 'granted') {
            new Notification('ポモドーロ完了！', {
                body: '休憩を取りましょう。'
            });
        }
    }
    
    /**
     * 時間表示を更新する
     */
    updateDisplay() {
        const minutes = Math.floor(this.remainingSeconds / 60);
        const seconds = this.remainingSeconds % 60;
        
        this.minutesDisplay.textContent = String(minutes).padStart(2, '0');
        this.secondsDisplay.textContent = String(seconds).padStart(2, '0');
    }
    
    /**
     * 円グラフの進捗を更新する
     */
    updateProgress() {
        const progress = this.remainingSeconds / this.totalSeconds;
        const offset = this.circumference * (1 - progress);
        this.progressCircle.style.strokeDashoffset = offset;
    }
    
    /**
     * 統計情報を更新する
     */
    updateStats() {
        this.completedCountDisplay.textContent = this.completedPomodoros;
        
        if (this.totalFocusMinutes >= 60) {
            const hours = Math.floor(this.totalFocusMinutes / 60);
            const mins = this.totalFocusMinutes % 60;
            this.totalTimeDisplay.textContent = `${hours}時間${mins}分`;
        } else {
            this.totalTimeDisplay.textContent = `${this.totalFocusMinutes}分`;
        }
    }
}

// DOMの読み込み完了後にタイマーを初期化
document.addEventListener('DOMContentLoaded', () => {
    new PomodoroTimer();
    
    // 通知の許可をリクエスト
    if ('Notification' in window && Notification.permission === 'default') {
        Notification.requestPermission();
    }
});
