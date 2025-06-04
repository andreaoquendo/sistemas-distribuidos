from flask import Flask, render_template
from flask_sse import sse
from apscheduler.schedulers.background import BackgroundScheduler