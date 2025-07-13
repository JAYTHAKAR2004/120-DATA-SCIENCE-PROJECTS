from flask import Flask, request, render_template
import pandas as pd
import neattext.functions as nfx
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.metrics.pairwise import cosine_similarity

from dashboard import getvaluecounts, getlevelcount, getsubjectsperlevel, yearwiseprofit

app = Flask(__name__)


# Data preprocessing functions
def getcosinemat(df):
    countvect = CountVectorizer()
    cvmat = countvect.fit_transform(df['Clean_title'])
    return cvmat


def getcleantitle(df):
    df['Clean_title'] = df['course_title'].apply(nfx.remove_stopwords)
    df['Clean_title'] = df['Clean_title'].apply(nfx.remove_special_characters)
    return df


def cosinesimmat(cv_mat):
    return cosine_similarity(cv_mat)


def readdata():
    return pd.read_csv('UdemyCleanedTitle.csv')


def recommend_course(df, title, cosine_mat, numrec):
    course_index = pd.Series(df.index, index=df['course_title']).drop_duplicates()
    index = course_index[title]
    scores = list(enumerate(cosine_mat[index]))
    sorted_scores = sorted(scores, key=lambda x: x[1], reverse=True)
    selected_course_index = [i[0] for i in sorted_scores[1:numrec + 1]]
    selected_course_score = [i[1] for i in sorted_scores[1:numrec + 1]]
    rec_df = df.iloc[selected_course_index]
    rec_df['Similarity_Score'] = selected_course_score
    return rec_df[['course_title', 'Similarity_Score', 'url', 'price', 'num_subscribers']]


def searchterm(term, df):
    result_df = df[df['course_title'].str.contains(term, case=False, na=False)]
    return result_df.sort_values(by='num_subscribers', ascending=False).head(6)


def extractfeatures(recdf):
    return list(recdf['url']), list(recdf['course_title']), list(recdf['price'])


@app.route('/', methods=['GET', 'POST'])
def hello_world():
    df = readdata()
    df = getcleantitle(df)

    if request.method == 'POST':
        titlename = request.form['course']
        try:
            cvmat = getcosinemat(df)
            cosine_mat = cosinesimmat(cvmat)
            recdf = recommend_course(df, titlename, cosine_mat, 6)
            course_url, course_title, course_price = extractfeatures(recdf)
            dictmap = dict(zip(course_title, course_url))
            return render_template('index.html', coursemap=dictmap, coursename=titlename, showtitle=True)

        except:
            resultdf = searchterm(titlename, df)
            if resultdf.empty:
                return render_template('index.html', showerror=True, coursename=titlename)
            course_url, course_title, course_price = extractfeatures(resultdf)
            coursemap = dict(zip(course_title, course_url))
            return render_template('index.html', coursemap=coursemap, coursename=titlename, showtitle=True)

    return render_template('index.html')

@app.route('/dashboard')
def dashboard():
    df = readdata()
    df = getcleantitle(df)

    # Convert all values to plain Python int
    valuecounts = {k: int(v) for k, v in getvaluecounts(df).items()}
    levelcounts = {k: int(v) for k, v in getlevelcount(df).items()}
    subjectsperlevel = {k: int(v) for k, v in getsubjectsperlevel(df).items()}

    profitmap, subscribersmap, profitmonthwise, monthwisesub = yearwiseprofit(df)

    # Also convert profit/subscriber maps
    profitmap = {str(k): float(v) for k, v in profitmap.items()}
    subscribersmap = {str(k): int(v) for k, v in subscribersmap.items()}
    profitmonthwise = {str(k): float(v) for k, v in profitmonthwise.items()}
    monthwisesub = {str(k): int(v) for k, v in monthwisesub.items()}

    return render_template(
        'dashboard.html',
        valuecounts=valuecounts,
        levelcounts=levelcounts,
        subjectsperlevel=subjectsperlevel,
        subscriberscountmap=subscribersmap,
        yearwiseprofitmap=profitmap,
        profitmonthwise=profitmonthwise,
        monthwisesub=monthwisesub
    )



if __name__ == '__main__':
    app.run(debug=True)
