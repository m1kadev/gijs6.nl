---
title: Goodbye Google Docs; hello Markdown
---

# Goodbye Google Documents; hello Markdown

After much hesitation, I finally made the switch: my summaries (*samenvattingen* in Dutch) are no longer in Google Docs. Instead, I've moved everything to my [own Jekyll-based site](https://school.gijs6.nl), hosted on GitHub Pages. I'm really happy with how it all turned out, and I wanted to share a bit of the process.

I had the idea of moving my summaries to Markdown for about 2 years, but I always thought it was just a big hassle and that it was not really worth it. But this year, I met Robin, and I saw that he had a [site with his own summaries](https://school.geheimesite.nl), and I thought it looked amazing and worked great. On a random day in a school vacation, I got motivated enough to actually start, so I started doing some research.

I didn't actually know much about working with serving Markdown files as nice HTML's and working with static site generators at the time, but after doing some research (aka reading some articles about static site generators and reading [the (quite bad) documentation of Jekyll](https://jekyllrb.com/docs)) it seemed quite doable.

At first, I tried using Flask on PythonAnywhere since I was familiar with it, but it wasn't great for local development and managing images and files. I also looked into Pelican, but that felt too clunky. Eventually, I gave Jekyll hosted on GitHub Pages a try, and it just clicked. It's really flexible and worked exactly how I wanted. And a problem that I had with using PythonAnywhere was syncing the files. For this site and this blog, I just push to GitHub and then pull on PythonAnywhere, which works, but it's not ideal. But the amazing thing about GitHub Pages is that I only have to push to GitHub, and everything just works.

I do not think it is entirely valid to just plainly compare Markdown to Google Docs or PDF's or Word or anything like that, because the goal of what they're trying to achieve is not the same. But honestly, Markdown just gives you so much more control and clarity. I wanted to use Markdown formatting, LaTeX for my math formulas, blockquotes (which is probably the best thing about Markdown), and I just wanted to be able to use CSS to make the summaries look great. With Google Docs, I always felt boxed in. It's made to be convenient, not powerful.

Before I had my site where I hosted the summaries completely myself, I referenced to all the Google Docs using another site that I had built earlier. But apart from my own summaries, I also collected WRTS lists (StudyGo is a stupid name), extra *oefentoetsen* (I don't really know the entirely correct English translation for that), and those kinds of things. That was actually quite hard to make on the Jekyll site, because it is not that easy to just use a custom backend, because well, there really isn't a backend. But I managed to get that kind of working with some clunky Python scripts.

> Jekyll is amazing, but Jekyll documentation is the opposite of amazing. The documentation kind of gets across what you can do with Jekyll, but there isn't a neat list of for example all the properties you can configure in your `_config.yml`. I really hope they improve the documentation in the future.

So all of that worked, and after [the first summary that I wrote completely in Markdown](https://school.gijs6.nl/4VWO/TW3/biol_h6), I was just completely amazed. I do not want to go back to Google Docs. It just feels like such a downgrade now.

There are, of course, a few features that were really easy to use in Google Docs, but are just not easy to use or even almost impossible to use in Markdown, but I got used to these changes really quickly.

Since then, I've also switched some other daily-use documents to Markdown, and I'm loving it. It's fast, it's customizable, and it just feels more *mine*. Google Docs, in comparison, feels bloated, slow, and honestly a bit soulless. But unfortunately, there are still situations where I have to use Google Docs, mostly when I'm collaborating with others. And unfortunately, my school probably won't like it if I submit a Markdown file (I should just try it i guess). For now, I still have to convert everything to PDF first (which I should probably automate).

I think my little switch to Markdown fits the bigger picture of the decisions that I and many others have made the last few years surrounding the internet and just technology in general. People are kind of done with big tech just being so incredibly powerful, and I am too. We depend on the technology of these companies every single day; never in the history of mankind have so few companies been so powerful. But that is an entire story on its own.
