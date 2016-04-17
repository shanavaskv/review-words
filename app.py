from flask import Flask, render_template, request, redirect
import simplejson as json
from operator import itemgetter
import datetime
from bokeh.embed import components
from bokeh.plotting import figure
from bokeh.resources import INLINE
from bokeh.util.string import encode_utf8

# from __future__ import print_function

app = Flask(__name__)
stopwords = ['a', 'about', 'after', 'all', 'also', 'am', 'an', 'and', 'any', 'are', 'as', 'at', 'back', 'be', 'because', 'been', 'better', 'bought', 'but', 'buy', 'by', 'can', "can't", 'could', 'did', 'do', 'does', "don't", 'even', 'first', 'for', 'from', 'get', 'go', 'good', 'got', 'great', 'had', 'has', 'have', 'how', "i'm", "i've", 'if', 'in', 'is', 'it', "it's", 'its', 'just', 'like', 'lot', 'love', 'many', 'me', 'more', 'most', 'much', 'my', 'need', 'new', 'no', 'not', 'now', 'of', 'on', 'one', 'only', 'or', 'other', 'out', 'product', 'really', 'so', 'some', 'still', 'tablet', 'take', 'than', 'that', 'the', 'them', 'then', 'there', 'they', 'thing', 'this', 'to', 'too', 'up', 'use', 'using', 'very', 'want', 'was', 'we','well', 'what', 'when', 'which', 'will', 'with', 'would', 'you', 'your', 'ipad']

plotkey = 'app'

def parse_text(text):
    d = {}
    for word in text.rsplit():
        if word.isdigit():
            continue
        wordL = word.lower()
        if wordL.endswith('.'):
            wordL = wordL[:-1]
        if len(wordL) < 2:
            continue
        if wordL in stopwords:
            continue

        try:
            d2 = d[wordL]
        except KeyError:
            d2 = 0
            d[wordL] = d2

        d[wordL] = d2 + 1

    for key in list(d.keys()):
        if key.endswith('s'):
            keys = key[:-1]
            if keys in d:
                d[keys] += d[key]
                del d[key]
    return d

@app.route('/')
def main():
  return redirect('/index')

@app.route('/index',methods=['GET', 'POST'])
def index():
    # if request.method == 'GET':
    return render_template('index.html')
    # else:
        # return redirect('/wcloud')

@app.route('/wcloud')
def wc():
    fid = open('static/tabs.json')
    reviews=''
    for dt in fid:
        data = json.loads(dt)
        if data['ProductInfo']['Name']:
            for rv in range(len(data['Reviews'])):
                if data['Reviews'][rv]['Content']:
                    if data['Reviews'][rv]['Content'].find('function()') < 0:
                        reviews = reviews + ' ' + data['Reviews'][rv]['Content']



    f = sorted(parse_text(reviews).items(),key=itemgetter(1),reverse=True)
    bwo = {}
    for c in range(30):
        bwo[str(f[c][0])] = f[c][1]
    return render_template('wcplot.html', wcdata=bwo)

@app.route('/wcpre')
def wcp():
    return render_template('showplot.html', title="Prealculated Word Cloud",imgplot="wcloud.png")

@app.route('/wctime_app')
def wtap():
    global plotkey
    plotkey = 'app'
    return redirect('/wctime')

@app.route('/wctime_price')
def wtpr():
    global plotkey
    plotkey = 'price'
    return redirect('/wctime')

@app.route('/wctime_screen')
def wtsc():
    global plotkey
    plotkey = 'screen'
    print plotkey
    return redirect('/wctime')

@app.route('/wctime')
def wt():
    fid = open('static/apple.json')
    reviews=''
    times=[]
    timrev=[]
    data = json.load(fid)
    for rv in range(len(data['Reviews'])):
        if data['Reviews'][rv]['Content']:
            if data['Reviews'][rv]['Content'].find('function()') < 0:
                times += [datetime.datetime.strptime(data['Reviews'][rv]['Date'],'%B %d, %Y')]
                timrev +=[parse_text(data['Reviews'][rv]['Content'])]
                reviews = reviews + ' ' + data['Reviews'][rv]['Content']

    timrev = [timrev[i[0]] for i in sorted(enumerate(times),key=lambda x:x[1])]
    times.sort()

    print plotkey
    dt = []
    for x in range(len(times)):
        try:
            dt += [timrev[x][plotkey]]
        except KeyError:
            dt += [0]

    x = list(range(0,10))
    fig = figure(title="Time evolution of: " + plotkey,x_axis_type="datetime")
    fig.line(times, dt, line_width=2)

    js_resources = INLINE.render_js()
    css_resources = INLINE.render_css()
    script, div = components(fig, INLINE)

    html = render_template('timeplot.html',
        js_resources=js_resources,
        css_resources=css_resources,
        plot_script=script,
        plot_div=div
        )

    return encode_utf8(html)

# @app.route('/page')
# def get_page():
#     return send_file('templates/progress.html')
#
# @app.route('/progress')
# def progress():
#     def generate():
#         x = 0
#         while x < 100:
#             print x
#             x = x + 10
#             # time.sleep(0.2)
#             yield "data:" + str(x) + "\n\n"
#     return Response(generate(), mimetype= 'text/event-stream')

if __name__ == '__main__':
    app.debug = True
    app.run(port=33507)
