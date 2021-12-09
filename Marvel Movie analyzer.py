import numpy as np
from empath import Empath
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
import csv
import matplotlib.pyplot as plt


# function to get sentiment of a sentence
def get_sentiment_scores(sentence):
    # Create a SentimentIntensityAnalyzer object.
    sid_obj = SentimentIntensityAnalyzer()

    # polarity_scores method of SentimentIntensityAnalyzer
    # object gives a sentiment dictionary.
    # which contains pos, neg, neu, and compound scores.

    # polarity_scores method of SentimentIntensityAnalyzer
    # object gives a sentiment dictionary.
    # which contains pos, neg, neu, and compound scores.

    # print("Overall sentiment dictionary is : ", sentiment_dict)
    # print("sentence was rated as ", sentiment_dict['neg'] * 100, "% Negative")
    # print("sentence was rated as ", sentiment_dict['neu'] * 100, "% Neutral")
    # print("sentence was rated as ", sentiment_dict['pos'] * 100, "% Positive")

    # print("Sentence Overall Rated As", end=" ")

    # decide sentiment as positive, negative and neutral
    # if sentiment_dict['compound'] >= 0.05:
    #   print("Positive")

    # elif sentiment_dict['compound'] <= - 0.05:
    #   print("Negative")

    return sid_obj.polarity_scores(sentence)


def get_empath_scores(sentence, cat_list, empath_lexicon):
    return empath_lexicon.analyze(sentence, categories=cat_list, normalize=True)


def get_empath_scores_no_categories(sentence, empath_lexicon):
    return empath_lexicon.analyze(sentence, normalize=True)


def get_rows(filename):
    # Open the file
    file = open(filename, encoding="utf8")

    # Link the file to a csv reader
    csvreader = csv.reader(file)

    # Create list for headers
    header = []
    header = next(csvreader)
    print(header)

    # Create list for rows
    rows = []
    for row in csvreader:
        rows.append(row)
    # print(rows)

    file.close()

    return rows


# Creates a scatter plot from the given values
# x is list of values, y is list of values, x_label is string, y_label is string, title is string, filename is string
def create_scatter_plot(x, y, x_label, y_label, title, filename):
    # plotting points as a scatter plot
    plt.scatter(x, y, color="black", marker="o", s=10)

    # x-axis label
    plt.xlabel(x_label)
    # frequency label
    plt.ylabel(y_label)
    # plot title
    plt.title(title)

    # Add a best fit line
    m, b = np.polyfit(x, y, 1)

    best_fit_x = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
    best_fit_y = []
    for x_num in best_fit_x:
        y_num = (m * x_num) + b
        best_fit_y.append(y_num)

    plt.plot(best_fit_x, best_fit_y, color='green', linestyle='dashed', linewidth=3, marker='o', markerfacecolor='blue',
             markersize=0, label='line of best fit (y = ' + str(round(m, 2)) + 'x + ' + str(round(b, 2)) + ')')

    # show a legend on the plot
    plt.legend()

    # function to show the plot
    fig1 = plt.gcf()
    plt.show()
    fig1.savefig('figures/' + filename, dpi=100)


if __name__ == '__main__':
    egc_rows = get_rows('endgame_critics.csv')
    egr_rows = get_rows('endgame_reviews.csv')
    iwc_rows = get_rows('infinity_critics.csv')
    iwr_rows = get_rows('infinity_reviews.csv')

    dict_of_list_of_rows = {'endgame_critics': egc_rows, 'endgame_reviews': egr_rows, 'infinity_critics': iwc_rows,
                            'infinity_reviews': iwr_rows}

    heading_strings = ['endgame_critics', 'endgame_reviews', 'infinity_critics', 'infinity_reviews']

    lexicon = Empath()

    # Build the category list based on most popular categories
    category_list = []

    total_critic_count_category_building = 0.0
    total_user_count_category_building = 0.0
    total_positive_count_category_building = 0.0
    total_lower_count_category_building = 0.0
    category_building_count_critics = {}
    category_building_count_users = {}
    category_building_count_positive = {}
    category_building_count_lower = {}

    for heading in heading_strings:
        print('building categories in ' + heading)
        # Get the list of rows to work on
        list_of_rows = dict_of_list_of_rows[heading]

        # Go over each individual review and process it
        for row in list_of_rows:
            # Get the review and score from the row
            review = row[2]
            score = float(row[4])

            empath_scores = get_empath_scores_no_categories(review, lexicon)
            if heading == 'endgame_critics' or heading == 'infinity_critics':
                score = score / 10

                total_critic_count_category_building = total_critic_count_category_building + 1.0
                for category in empath_scores:
                    if category in category_building_count_critics:
                        category_building_count_critics[category] = category_building_count_critics[category] + empath_scores[category]
                    else:
                        category_building_count_critics[category] = empath_scores[category]
            else:
                total_user_count_category_building = total_user_count_category_building + 1.0
                for category in empath_scores:
                    if category in category_building_count_users:
                        category_building_count_users[category] = category_building_count_users[category] + \
                                                                    empath_scores[category]
                    else:
                        category_building_count_users[category] = empath_scores[category]

            if score < 7:
                total_lower_count_category_building = total_lower_count_category_building + 1.0
                for category in empath_scores:
                    if category in category_building_count_lower:
                        category_building_count_lower[category] = category_building_count_lower[category] + empath_scores[category]
                    else:
                        category_building_count_lower[category] = empath_scores[category]
            else:
                total_positive_count_category_building = total_positive_count_category_building + 1.0
                for category in empath_scores:
                    if category in category_building_count_positive:
                        category_building_count_positive[category] = category_building_count_positive[category] + \
                                                                    empath_scores[category]
                    else:
                        category_building_count_positive[category] = empath_scores[category]

    # Doing the averaging
    for category in category_building_count_critics:
        category_building_count_critics[category] = category_building_count_critics[category] / total_critic_count_category_building

    for category in category_building_count_users:
        category_building_count_users[category] = category_building_count_users[category] / total_user_count_category_building

    for category in category_building_count_positive:
        category_building_count_positive[category] = category_building_count_positive[category] / total_positive_count_category_building

    for category in category_building_count_lower:
        category_building_count_lower[category] = category_building_count_lower[category] / total_lower_count_category_building

    # Now determine the tops of the lists
    print('Doing top twenty for critics')
    top_twenty_categories_critics = [['word', 0]]
    for category in category_building_count_critics:
        print(category)
        for i in range(len(top_twenty_categories_critics)):
            if category_building_count_critics[category] > top_twenty_categories_critics[i][1]:
                top_twenty_categories_critics.insert(i, [category, category_building_count_critics[category]])
                break
        if len(top_twenty_categories_critics) > 20:
            top_twenty_categories_critics.pop()

    print('Doing top twenty for users')
    top_twenty_categories_users = [['word', 0]]
    for category in category_building_count_users:
        for i in range(len(top_twenty_categories_users)):
            if category_building_count_users[category] > top_twenty_categories_users[i][1]:
                top_twenty_categories_users.insert(i, [category, category_building_count_users[category]])
                break
        if len(top_twenty_categories_users) > 20:
            top_twenty_categories_users.pop()

    print('Doing top twenty for positive')
    top_twenty_categories_positive = [['word', 0]]
    for category in category_building_count_positive:
        for i in range(len(top_twenty_categories_positive)):
            if category_building_count_positive[category] > top_twenty_categories_positive[i][1]:
                top_twenty_categories_positive.insert(i, [category, category_building_count_positive[category]])
                break
        if len(top_twenty_categories_positive) > 20:
            top_twenty_categories_positive.pop()

    print('Doing top twenty for lower')
    top_twenty_categories_lower = [['word', 0]]
    for category in category_building_count_lower:
        for i in range(len(top_twenty_categories_lower)):
            if category_building_count_lower[category] > top_twenty_categories_lower[i][1]:
                top_twenty_categories_lower.insert(i, [category, category_building_count_lower[category]])
                break
        if len(top_twenty_categories_lower) > 20:
            top_twenty_categories_lower.pop()

    print("Top categories for critics: ")
    print(top_twenty_categories_critics)
    for category in top_twenty_categories_critics:
        category_list.append(category[0])

    print("Top categories for average viewers: ")
    print(top_twenty_categories_users)
    for category in top_twenty_categories_users:
        if category[0] not in category_list:
            category_list.append(category[0])

    print("Top categories for positive reviews: ")
    print(top_twenty_categories_positive)
    for category in top_twenty_categories_positive:
        if category[0] not in category_list:
            category_list.append(category[0])

    print("Top categories for lower scores: ")
    print(top_twenty_categories_lower)
    for category in top_twenty_categories_lower:
        if category[0] not in category_list:
            category_list.append(category[0])

    print('category_list built: ')
    print(category_list)

    x_axis_user_scores = {'endgame_critics': [], 'endgame_reviews': [], 'infinity_critics': [], 'infinity_reviews': []}
    y_axis_VADER_scores = {'endgame_critics': [], 'endgame_reviews': [], 'infinity_critics': [], 'infinity_reviews': []}

    # set up storage for empath category scores
    y_axis_topic_scores = {'endgame_critics': {}, 'endgame_reviews': {}, 'infinity_critics': {}, 'infinity_reviews': {}}

    for heading in heading_strings:
        for category in category_list:
            y_axis_topic_scores[heading][category] = []

    # set up storage for score averages
    review_score_averages = {}
    compound_score_averages = {}

    # set up storage for topic frequency averages i.e. overall topic frequency
    topic_freq_averages = {'endgame_critics': {}, 'endgame_reviews': {}, 'infinity_critics': {}, 'infinity_reviews': {}}

    for heading in heading_strings:
        # Get the list of rows to work on
        list_of_rows = dict_of_list_of_rows[heading]

        # initialize items used for computing topic frequencies to 0
        total_review_count_under_heading = 0.0
        category_totals_under_heading = {}

        for category in category_list:
            category_totals_under_heading[category] = 0.0

        # initialize items for other averaging to 0
        review_score_sum_under_heading = 0.0
        compound_score_sum_under_heading = 0.0

        # Go over each individual review and process it
        for row in list_of_rows:
            # Add 1 to count of how many reviews
            total_review_count_under_heading = total_review_count_under_heading + 1.0

            # Get the review and score from the row
            review = row[2]
            score = float(row[4])

            # user reviews are out of 10 while critic reviews are out of 100: multiple user scores, so they're all
            # out of 100
            if not heading == 'endgame_reviews' and not heading == 'infinity_reviews':
                score = score / 10

            # Compute additional scores with VADER and Empath
            sentiment_scores = get_sentiment_scores(review)
            empath_scores = get_empath_scores(review, category_list, lexicon)

            # Add data points to be plotted
            # x value is always the score the user gave the movie
            x_axis_user_scores[heading].append(score)

            # Add VADER score (y)
            # Making compound scores range from -1 to 1, so it is more obvious when something is negative vs positive
            compound_score = sentiment_scores['compound']
            y_axis_VADER_scores[heading].append(compound_score)

            # Add Empath topic scores (y)
            for category in category_list:
                y_axis_topic_scores[heading][category].append(empath_scores[category])

            # Add topic frequencies to totals for later averaging
            for category in category_list:
                category_totals_under_heading[category] = category_totals_under_heading[category] + empath_scores[
                    category]

            # Add review score for later averaging
            review_score_sum_under_heading = review_score_sum_under_heading + float(score)

            # Add compound score for later averaging
            compound_score_sum_under_heading = compound_score_sum_under_heading + compound_score

        # Compute review score average
        review_score_averages[heading] = review_score_sum_under_heading / total_review_count_under_heading

        # Compute compound score average
        compound_score_averages[heading] = compound_score_sum_under_heading / total_review_count_under_heading

        # Compute avg topic frequencies
        for category in category_list:
            topic_freq_averages[heading][category] = category_totals_under_heading[
                                                         category] / total_review_count_under_heading

        # Print out the total number for stuff:
        print(str(total_review_count_under_heading) + " reviews in " + heading)

    # We should now have ALL the necessary data: output some plots and shit
    # Create compound score plots
    for heading in heading_strings:
        create_scatter_plot(x_axis_user_scores[heading], y_axis_VADER_scores[heading], 'Score given on Metacritic',
                            "Sentiment Score", 'Review Score vs. Sentiment Score for ' + heading,
                            heading + '_sentiment_score_plot.png')

    # Create topic occurrence plots
    for category in category_list:
        for heading in heading_strings:
            create_scatter_plot(x_axis_user_scores[heading], y_axis_topic_scores[heading][category],
                                'Score given on Metacritic', "Topic frequency",
                                'Review Score vs. Frequency of ' + category + ' for ' + heading,
                                heading + '_' + category + '_frequency_plot.png')

    # Print out averages in the console
    for heading in heading_strings:
        print('Average ' + heading + ' sentiment according to VADER: ' + str(compound_score_averages[heading]))

    for heading in heading_strings:
        print('Average ' + heading + ' review score: ' + str(review_score_averages[heading]))

    for category in category_list:
        for heading in heading_strings:
            print('Average frequency of ' + category + ' in ' + heading + ' : ' + str(
                topic_freq_averages[heading][category]))
