"""
Flask Timer API for timer state retrieval and control.
All API responses are in JSON format.
"""

from flask import Flask, jsonify, request
from timer import Timer


def create_app(mock_mode: bool = False) -> Flask:
    """
    Create and configure the Flask application.
    
    Args:
        mock_mode: If True, use mock timer for testing.
        
    Returns:
        Configured Flask application.
    """
    app = Flask(__name__)
    
    # Create timer instance (singleton for the app)
    timer = Timer(mock_mode=mock_mode)
    
    # Store timer in app config for access in routes
    app.config['TIMER'] = timer
    
    @app.route('/api/timer', methods=['GET'])
    def get_timer_state():
        """
        Get current timer state.
        
        Returns:
            JSON response with timer state data.
        """
        timer_instance = app.config['TIMER']
        data = timer_instance.get_data()
        return jsonify({
            "success": True,
            "data": data.to_dict()
        })
    
    @app.route('/api/timer/start', methods=['POST'])
    def start_timer():
        """
        Start the timer with specified duration.
        
        Request body:
            {"duration_seconds": <float>}
            
        Returns:
            JSON response with success status and timer data.
        """
        timer_instance = app.config['TIMER']
        
        # Parse request data
        request_data = request.get_json(silent=True)
        if request_data is None:
            return jsonify({
                "success": False,
                "error": "Request body is required"
            }), 400
        
        duration = request_data.get('duration_seconds')
        if duration is None:
            return jsonify({
                "success": False,
                "error": "duration_seconds is required"
            }), 400
        
        try:
            duration = float(duration)
        except (TypeError, ValueError):
            return jsonify({
                "success": False,
                "error": "duration_seconds must be a number"
            }), 400
        
        if duration <= 0:
            return jsonify({
                "success": False,
                "error": "duration_seconds must be positive"
            }), 400
        
        success = timer_instance.start(duration)
        data = timer_instance.get_data()
        
        return jsonify({
            "success": success,
            "data": data.to_dict()
        })
    
    @app.route('/api/timer/pause', methods=['POST'])
    def pause_timer():
        """
        Pause the running timer.
        
        Returns:
            JSON response with success status and timer data.
        """
        timer_instance = app.config['TIMER']
        success = timer_instance.pause()
        data = timer_instance.get_data()
        
        if not success:
            return jsonify({
                "success": False,
                "error": "Timer is not running",
                "data": data.to_dict()
            }), 400
        
        return jsonify({
            "success": True,
            "data": data.to_dict()
        })
    
    @app.route('/api/timer/resume', methods=['POST'])
    def resume_timer():
        """
        Resume a paused timer.
        
        Returns:
            JSON response with success status and timer data.
        """
        timer_instance = app.config['TIMER']
        success = timer_instance.resume()
        data = timer_instance.get_data()
        
        if not success:
            return jsonify({
                "success": False,
                "error": "Timer is not paused",
                "data": data.to_dict()
            }), 400
        
        return jsonify({
            "success": True,
            "data": data.to_dict()
        })
    
    @app.route('/api/timer/stop', methods=['POST'])
    def stop_timer():
        """
        Stop the timer and reset to idle state.
        
        Returns:
            JSON response with success status and timer data.
        """
        timer_instance = app.config['TIMER']
        success = timer_instance.stop()
        data = timer_instance.get_data()
        
        if not success:
            return jsonify({
                "success": False,
                "error": "Timer is already idle",
                "data": data.to_dict()
            }), 400
        
        return jsonify({
            "success": True,
            "data": data.to_dict()
        })
    
    @app.route('/api/timer/reset', methods=['POST'])
    def reset_timer():
        """
        Reset the timer to initial duration and restart running.
        This restores the original duration AND starts the timer.
        
        Returns:
            JSON response with success status and timer data.
        """
        timer_instance = app.config['TIMER']
        success = timer_instance.reset()
        data = timer_instance.get_data()
        
        if not success:
            return jsonify({
                "success": False,
                "error": "No timer duration set",
                "data": data.to_dict()
            }), 400
        
        return jsonify({
            "success": True,
            "data": data.to_dict()
        })
    
    return app


# Application entry point
app = create_app()


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
