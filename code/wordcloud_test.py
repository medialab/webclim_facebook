import matplotlib.pyplot as plt
from wordcloud import WordCloud

text = """
Introduction

Since the 2016 American elections, the web platforms are under pressure to regulate misinformation. Facebook has publicly announced a three-part policy to fight against ‘misleading or harmful content’ : they remove harmful information, reduce the spread of misinformation and inform people with additional context [1]. The application of the inform policy can be transparently verified on Facebook, with some posts being publicly labeled as misinformation, and Facebook communicates regularly about removing violent or misinformative accounts, groups or pages [2, 3], but less is known about the reduce policy. Our aim was to investigate whether the reduce measures are actually enforced.


Methodology

For this, we investigated pages that publicly claimed to have their distribution reduced by Facebook and that shared the screenshot Facebook message as a proof. We already knew a few pages doing so from our fact-checking experience (“Mark Levin” and “100 Percent FED Up”), and we searched for more self-declared repeat offender pages using the CrowdTangle API. 

We used the ‘/posts/search’ endpoint of the API on November 25, 2020, with the following keywords:
‘reduced distribution’ AND (‘restricted’ OR ‘censored’ OR ‘silenced’)
‘Your page has a reduced distribution’

"""

wordcloud = WordCloud(background_color="black").generate(text)

fig = plt.figure(figsize=(10, 5))

plt.imshow(wordcloud, interpolation="bilinear")
plt.axis("off")
plt.tight_layout(pad=0)
fig.savefig('wordcloud.png', dpi=fig.dpi)
plt.show()
