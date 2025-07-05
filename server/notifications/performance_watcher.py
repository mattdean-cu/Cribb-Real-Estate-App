from abc import ABC, abstractmethod
from typing import List, Dict, Any
from datetime import datetime
import sys
import os

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.exceptions import CribbException


class NotificationException(CribbException):
    """Exception for notification system errors"""
    pass


class PropertyAlert:
    """Data class for property performance alerts"""

    def __init__(self, property_id: str, alert_type: str, message: str,
                 threshold: float, actual_value: float, severity: str = 'warning'):
        self.property_id = property_id
        self.alert_type = alert_type  # 'low_roi', 'high_vacancy', etc.
        self.message = message
        self.threshold = threshold
        self.actual_value = actual_value
        self.severity = severity  # 'info', 'warning', 'critical'
        self.timestamp = datetime.now()
        self.acknowledged = False

    def to_dict(self) -> Dict[str, Any]:
        """Convert alert to dictionary for JSON serialization"""
        return {
            'property_id': self.property_id,
            'alert_type': self.alert_type,
            'message': self.message,
            'threshold': self.threshold,
            'actual_value': self.actual_value,
            'severity': self.severity,
            'timestamp': self.timestamp.isoformat(),
            'acknowledged': self.acknowledged
        }

    def acknowledge(self):
        """Mark alert as acknowledged"""
        self.acknowledged = True


class AlertObserver(ABC):
    """Abstract base class for alert observers"""

    @abstractmethod
    def notify(self, alert: PropertyAlert):
        """Handle an alert notification"""
        pass


class EmailNotifier(AlertObserver):
    """Send alerts via email"""

    def __init__(self, email_service=None):
        self.email_service = email_service

    def notify(self, alert: PropertyAlert):
        """Send email notification"""
        if not self.email_service:
            print(f"📧 EMAIL ALERT: {alert.message}")
            return

        # TODO: Integrate with actual email service
        subject = f"Property Alert: {alert.alert_type.replace('_', ' ').title()}"
        body = f"""
        Property Alert

        Property: {alert.property_id}
        Alert Type: {alert.alert_type}
        Severity: {alert.severity}

        {alert.message}

        Threshold: {alert.threshold}
        Actual Value: {alert.actual_value}
        Time: {alert.timestamp}
        """

        print(f"📧 Sending email: {subject}")


class DatabaseNotifier(AlertObserver):
    """Store alerts in database"""

    def notify(self, alert: PropertyAlert):
        """Save alert to database"""
        # TODO: Implement database storage
        print(f"💾 Saving alert to database: {alert.alert_type} for {alert.property_id}")


class WebhookNotifier(AlertObserver):
    """Send alerts to webhook endpoint"""

    def __init__(self, webhook_url: str):
        self.webhook_url = webhook_url

    def notify(self, alert: PropertyAlert):
        """Send alert to webhook"""
        # TODO: Implement webhook posting
        print(f"🔗 Sending webhook to {self.webhook_url}: {alert.message}")


class PerformanceWatcher:
    """Observer pattern implementation for property performance monitoring"""

    def __init__(self):
        self.observers: List[AlertObserver] = []
        self.active_alerts: List[PropertyAlert] = []

        # Default thresholds - will be configurable later
        self.min_roi_threshold = 8.0
        self.min_cap_rate_threshold = 6.0

    def add_observer(self, observer: AlertObserver):
        """Add an alert observer"""
        if observer not in self.observers:
            self.observers.append(observer)

    def remove_observer(self, observer: AlertObserver):
        """Remove an alert observer"""
        if observer in self.observers:
            self.observers.remove(observer)

    def notify_observers(self, alert: PropertyAlert):
        """Notify all observers of an alert"""
        self.active_alerts.append(alert)

        for observer in self.observers:
            try:
                observer.notify(alert)
            except Exception as e:
                print(f"❌ Error notifying observer {observer.__class__.__name__}: {e}")

    def check_property_performance(self, property_data: Dict[str, Any],
                                   simulation_results: Dict[str, Any]):
        """Check property performance and generate alerts if needed"""
        property_id = property_data.get('id', 'unknown')

        # Check ROI performance
        roi = simulation_results.get('annual_roi', 0)
        if roi < self.min_roi_threshold:
            alert = PropertyAlert(
                property_id=property_id,
                alert_type='low_roi',
                message=f"Property ROI ({roi:.2f}%) is below threshold ({self.min_roi_threshold}%)",
                threshold=self.min_roi_threshold,
                actual_value=roi,
                severity='warning' if roi > self.min_roi_threshold * 0.8 else 'critical'
            )
            self.notify_observers(alert)

        # Check cap rate performance
        cap_rate = simulation_results.get('cap_rate', 0)
        if cap_rate < self.min_cap_rate_threshold:
            alert = PropertyAlert(
                property_id=property_id,
                alert_type='low_cap_rate',
                message=f"Property cap rate ({cap_rate:.2f}%) is below threshold ({self.min_cap_rate_threshold}%)",
                threshold=self.min_cap_rate_threshold,
                actual_value=cap_rate,
                severity='warning'
            )
            self.notify_observers(alert)

        # Check negative cash flow
        monthly_cash_flow = simulation_results.get('monthly_cash_flow', 0)
        if monthly_cash_flow < 0:
            alert = PropertyAlert(
                property_id=property_id,
                alert_type='negative_cash_flow',
                message=f"Property has negative cash flow: ${monthly_cash_flow:.2f}/month",
                threshold=0,
                actual_value=monthly_cash_flow,
                severity='critical'
            )
            self.notify_observers(alert)

    def get_active_alerts(self, property_id: str = None) -> List[PropertyAlert]:
        """Get active alerts, optionally filtered by property"""
        if property_id:
            return [alert for alert in self.active_alerts
                    if alert.property_id == property_id and not alert.acknowledged]
        return [alert for alert in self.active_alerts if not alert.acknowledged]

    def acknowledge_alert(self, alert_index: int):
        """Acknowledge an alert by index"""
        if 0 <= alert_index < len(self.active_alerts):
            self.active_alerts[alert_index].acknowledge()

    def clear_acknowledged_alerts(self):
        """Remove acknowledged alerts from active list"""
        self.active_alerts = [alert for alert in self.active_alerts
                              if not alert.acknowledged]


# Convenience function for easy setup
def setup_performance_monitoring(email_enabled=False, database_enabled=True,
                                 webhook_url=None) -> PerformanceWatcher:
    """Set up performance monitoring with specified notifiers"""
    watcher = PerformanceWatcher()

    if email_enabled:
        watcher.add_observer(EmailNotifier())

    if database_enabled:
        watcher.add_observer(DatabaseNotifier())

    if webhook_url:
        watcher.add_observer(WebhookNotifier(webhook_url))

    return watcher