from s4e.config import *
from s4e.task import Task

class Job(Task):
   def run(self):
       asset = self.asset
       self.output['detail'] = []  # It is detailed result from job
       self.output['compact'] = []  # It is short result from job
       self.output['video'] = []  # It is the steps, commands, etc for doing the job

   def calculate_score(self):
       # It is a number between 0 and 10
       # if score == 1  information
       # if 1 < score < 4 low
       # if 4 <= score < 7 medium
       # if 7 <= score < 9 high
       # if 9 <= score < 11 critical
       # set score to something meaningful
       self.score = self.param['max_score'] 