import whisper_timestamped as whisper
import ffmpeg
import re
import os.path

INPUT_FILE = '60secafrica.webm'

model = whisper.load_model("tiny")
result = whisper.transcribe(model, INPUT_FILE)

sentence = "Stop jamal for 60 seconds in africa".lower().split(' ')
times = [{'text':'','start':0,'end':0,'confidence':0} for _ in sentence]
for segment in result['segments']:
  for word in segment['words']:
    w = "".join(re.split("[^a-zA-Z0-9]*", word['text'])).lower()
    if w in sentence:
      index = sentence.index(w)
      if word['confidence'] > times[index]['confidence'] or word['end']-word['start'] > times[index]['end'] - times[index]['start']:
        times[index] = word
        times[index]['text'] = w

[print(x) for x in times]

names = []
OFFSET = 0.1
DIR = 'tmp/'
if not os.path.exists(DIR):
  os.makedirs(DIR)

for i, word in enumerate(times):
  name = DIR + word['text']
  if word:
    if not os.path.isfile(name + '.mkv'):
      input = ffmpeg.input(INPUT_FILE, ss=word['start']-OFFSET)
      processAudio = (
        input.audio
        .filter('atrim', duration=word['end']-word['start']+OFFSET)
        .filter('asetpts','(PTS-STARTPTS)')
        .output(name + '_a.mp3')
        .run()
      )
      processVideo = (
        input.video
        .trim(start=0, duration=word['end']-word['start']+OFFSET+0.3)
        .setpts('(PTS-STARTPTS)')
        .output(name + '_v.mkv')
        .run()
      )
      out = ffmpeg.output(ffmpeg.input(name + '_a.mp3').audio, ffmpeg.input(name + '_v.mkv').video, name + '.mkv').run()
    names.append(name + '.mkv')

final_name = "".join(sentence) + '.mkv'
if not os.path.isfile(final_name):
  p = ffmpeg.filter([ffmpeg.input(x) for x in names], 'concat', a=1, v=1, n=len(names)).output(final_name)
  print(p.compile())
  p.run()