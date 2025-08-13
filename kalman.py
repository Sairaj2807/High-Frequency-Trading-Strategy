import numpy as np

class KalmanFilter:
    def __init__(self):
        self.A = np.array([[1]])
        self.C = np.array([[1]])
        self.Q = np.array([[0.0001]])
        self.R = np.array([[0.01]])
        self.P = np.array([[1]])
        self.x = np.array([[0]])
        self.ticks = 0

    def update(self, y):
        self.ticks += 1
        # Prediction
        x_pred = self.A @ self.x
        P_pred = self.A @ self.P @ self.A.T + self.Q

        # Kalman Gain
        K = P_pred @ self.C.T @ np.linalg.inv(self.C @ P_pred @ self.C.T + self.R)

        # Update estimate
        self.x = x_pred + K @ (y - self.C @ x_pred)
        self.P = (np.eye(self.A.shape[0]) - K @ self.C) @ P_pred

        return self.x[0, 0]
