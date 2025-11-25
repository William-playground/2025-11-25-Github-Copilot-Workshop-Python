"""
Tests for Timer module and Timer API.
"""

import pytest
from timer import Timer, TimerState, TimerData
from timer_api import create_app


class TestTimer:
    """Test cases for Timer class."""
    
    def test_initial_state(self):
        """Test timer initializes in idle state."""
        timer = Timer(mock_mode=True)
        assert timer.get_state() == TimerState.IDLE
        data = timer.get_data()
        assert data.state == "idle"
        assert data.remaining_seconds == 0.0
        assert data.total_seconds == 0.0
    
    def test_start_timer(self):
        """Test starting the timer."""
        timer = Timer(mock_mode=True)
        timer.set_mock_time(0.0)
        
        result = timer.start(60.0)
        assert result is True
        assert timer.get_state() == TimerState.RUNNING
        
        data = timer.get_data()
        assert data.state == "running"
        assert data.remaining_seconds == 60.0
        assert data.total_seconds == 60.0
    
    def test_start_with_invalid_duration(self):
        """Test starting with invalid duration."""
        timer = Timer(mock_mode=True)
        
        assert timer.start(0) is False
        assert timer.start(-10) is False
        assert timer.get_state() == TimerState.IDLE
    
    def test_pause_timer(self):
        """Test pausing the timer."""
        timer = Timer(mock_mode=True)
        timer.set_mock_time(0.0)
        timer.start(60.0)
        
        timer.advance_mock_time(10.0)
        result = timer.pause()
        
        assert result is True
        assert timer.get_state() == TimerState.PAUSED
        
        data = timer.get_data()
        assert data.state == "paused"
        assert data.remaining_seconds == 50.0
    
    def test_pause_when_not_running(self):
        """Test pausing when timer is not running."""
        timer = Timer(mock_mode=True)
        
        assert timer.pause() is False
        assert timer.get_state() == TimerState.IDLE
    
    def test_resume_timer(self):
        """Test resuming the timer."""
        timer = Timer(mock_mode=True)
        timer.set_mock_time(0.0)
        timer.start(60.0)
        
        timer.advance_mock_time(10.0)
        timer.pause()
        
        timer.advance_mock_time(5.0)
        result = timer.resume()
        
        assert result is True
        assert timer.get_state() == TimerState.RUNNING
        
        data = timer.get_data()
        assert data.remaining_seconds == 50.0
    
    def test_resume_when_not_paused(self):
        """Test resuming when timer is not paused."""
        timer = Timer(mock_mode=True)
        
        assert timer.resume() is False
    
    def test_stop_timer(self):
        """Test stopping the timer."""
        timer = Timer(mock_mode=True)
        timer.set_mock_time(0.0)
        timer.start(60.0)
        
        result = timer.stop()
        
        assert result is True
        assert timer.get_state() == TimerState.IDLE
        
        data = timer.get_data()
        assert data.state == "idle"
        assert data.remaining_seconds == 0.0
    
    def test_stop_when_already_idle(self):
        """Test stopping when timer is already idle."""
        timer = Timer(mock_mode=True)
        
        assert timer.stop() is False
    
    def test_reset_timer(self):
        """Test resetting the timer."""
        timer = Timer(mock_mode=True)
        timer.set_mock_time(0.0)
        timer.start(60.0)
        
        timer.advance_mock_time(30.0)
        result = timer.reset()
        
        assert result is True
        assert timer.get_state() == TimerState.RUNNING
        
        data = timer.get_data()
        assert data.remaining_seconds == 60.0
    
    def test_reset_without_duration(self):
        """Test resetting without prior duration."""
        timer = Timer(mock_mode=True)
        
        assert timer.reset() is False
    
    def test_timer_expires(self):
        """Test timer expires when time runs out."""
        timer = Timer(mock_mode=True)
        timer.set_mock_time(0.0)
        timer.start(10.0)
        
        timer.advance_mock_time(15.0)
        
        assert timer.get_state() == TimerState.IDLE
        
        data = timer.get_data()
        assert data.remaining_seconds == 0.0
    
    def test_timer_data_to_dict(self):
        """Test TimerData to_dict method."""
        data = TimerData(state="running", remaining_seconds=45.5, total_seconds=60.0)
        
        result = data.to_dict()
        
        assert result == {
            "state": "running",
            "remaining_seconds": 45.5,
            "total_seconds": 60.0
        }


class TestTimerAPI:
    """Test cases for Timer API."""
    
    @pytest.fixture
    def client(self):
        """Create test client."""
        app = create_app(mock_mode=True)
        app.config['TESTING'] = True
        with app.test_client() as client:
            yield client
    
    @pytest.fixture
    def app_with_timer(self):
        """Create app with accessible timer."""
        app = create_app(mock_mode=True)
        app.config['TESTING'] = True
        return app
    
    def test_get_timer_state(self, client):
        """Test GET /api/timer returns timer state."""
        response = client.get('/api/timer')
        
        assert response.status_code == 200
        data = response.get_json()
        assert data['success'] is True
        assert 'data' in data
        assert data['data']['state'] == 'idle'
    
    def test_start_timer(self, client):
        """Test POST /api/timer/start starts the timer."""
        response = client.post(
            '/api/timer/start',
            json={'duration_seconds': 60}
        )
        
        assert response.status_code == 200
        data = response.get_json()
        assert data['success'] is True
        assert data['data']['state'] == 'running'
        assert data['data']['total_seconds'] == 60.0
    
    def test_start_timer_without_body(self, client):
        """Test POST /api/timer/start without body."""
        response = client.post(
            '/api/timer/start',
            content_type='application/json'
        )
        
        assert response.status_code == 400
        data = response.get_json()
        assert data['success'] is False
        assert 'error' in data
    
    def test_start_timer_without_duration(self, client):
        """Test POST /api/timer/start without duration."""
        response = client.post(
            '/api/timer/start',
            json={'other_field': 'value'}
        )
        
        assert response.status_code == 400
        data = response.get_json()
        assert data['success'] is False
        assert 'duration_seconds is required' in data['error']
    
    def test_start_timer_with_invalid_duration(self, client):
        """Test POST /api/timer/start with invalid duration."""
        response = client.post(
            '/api/timer/start',
            json={'duration_seconds': 'invalid'}
        )
        
        assert response.status_code == 400
        data = response.get_json()
        assert data['success'] is False
    
    def test_start_timer_with_negative_duration(self, client):
        """Test POST /api/timer/start with negative duration."""
        response = client.post(
            '/api/timer/start',
            json={'duration_seconds': -10}
        )
        
        assert response.status_code == 400
        data = response.get_json()
        assert data['success'] is False
    
    def test_pause_timer(self, app_with_timer):
        """Test POST /api/timer/pause pauses the timer."""
        with app_with_timer.test_client() as client:
            # Start timer first
            timer = app_with_timer.config['TIMER']
            timer.set_mock_time(0.0)
            client.post('/api/timer/start', json={'duration_seconds': 60})
            
            response = client.post('/api/timer/pause')
            
            assert response.status_code == 200
            data = response.get_json()
            assert data['success'] is True
            assert data['data']['state'] == 'paused'
    
    def test_pause_timer_when_not_running(self, client):
        """Test POST /api/timer/pause when not running."""
        response = client.post('/api/timer/pause')
        
        assert response.status_code == 400
        data = response.get_json()
        assert data['success'] is False
        assert 'not running' in data['error']
    
    def test_resume_timer(self, app_with_timer):
        """Test POST /api/timer/resume resumes the timer."""
        with app_with_timer.test_client() as client:
            timer = app_with_timer.config['TIMER']
            timer.set_mock_time(0.0)
            
            client.post('/api/timer/start', json={'duration_seconds': 60})
            client.post('/api/timer/pause')
            
            response = client.post('/api/timer/resume')
            
            assert response.status_code == 200
            data = response.get_json()
            assert data['success'] is True
            assert data['data']['state'] == 'running'
    
    def test_resume_timer_when_not_paused(self, client):
        """Test POST /api/timer/resume when not paused."""
        response = client.post('/api/timer/resume')
        
        assert response.status_code == 400
        data = response.get_json()
        assert data['success'] is False
        assert 'not paused' in data['error']
    
    def test_stop_timer(self, app_with_timer):
        """Test POST /api/timer/stop stops the timer."""
        with app_with_timer.test_client() as client:
            timer = app_with_timer.config['TIMER']
            timer.set_mock_time(0.0)
            
            client.post('/api/timer/start', json={'duration_seconds': 60})
            
            response = client.post('/api/timer/stop')
            
            assert response.status_code == 200
            data = response.get_json()
            assert data['success'] is True
            assert data['data']['state'] == 'idle'
    
    def test_stop_timer_when_already_idle(self, client):
        """Test POST /api/timer/stop when already idle."""
        response = client.post('/api/timer/stop')
        
        assert response.status_code == 400
        data = response.get_json()
        assert data['success'] is False
        assert 'already idle' in data['error']
    
    def test_reset_timer(self, app_with_timer):
        """Test POST /api/timer/reset resets the timer."""
        with app_with_timer.test_client() as client:
            timer = app_with_timer.config['TIMER']
            timer.set_mock_time(0.0)
            
            client.post('/api/timer/start', json={'duration_seconds': 60})
            timer.advance_mock_time(30.0)
            
            response = client.post('/api/timer/reset')
            
            assert response.status_code == 200
            data = response.get_json()
            assert data['success'] is True
            assert data['data']['state'] == 'running'
            assert data['data']['remaining_seconds'] == 60.0
    
    def test_reset_timer_without_duration(self, client):
        """Test POST /api/timer/reset without duration set."""
        response = client.post('/api/timer/reset')
        
        assert response.status_code == 400
        data = response.get_json()
        assert data['success'] is False
        assert 'No timer duration' in data['error']
    
    def test_json_response_format(self, client):
        """Test that all responses are JSON format."""
        response = client.get('/api/timer')
        
        assert response.content_type == 'application/json'
