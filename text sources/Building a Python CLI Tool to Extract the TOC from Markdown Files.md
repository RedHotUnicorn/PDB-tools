At the end of the article, you will find other useful resources which you may be interested in using.

Throughout the article I will use the word library to mean your entire digital knowledge (library), which is used interchangeably with “Obsidian Vault” or “Zettelkasten”.

This collection of tips is my current solution to problems I’ve encountered throughout my PhD and is by no means perfect/complete. If you have any additional tips or feedback, feel free to comment or contact me. I’ll try to keep this article up-to-date.

Here, I show how I use Obsidian ( https://obsidian.md) as a PhD student in Artificial Intelligence and the workflows I’ve found to manage my knowledge.

Knowledge is the most powerful tool you have as a researcher. Knowledge, however, is worthless if it cannot be accessed quickly and effectively. The key is in a consistent and easy-to-use method of archiving information so that taking notes becomes an effortless and pleasing experience.

Tools and workflows for managing your zettelkasten, projects, reading lists, notes, and inspiration during your PhD.

1. Philosophy: How to take and organize notes effectively

“If you wish to make an apple pie from scratch, you must first invent the universe” — Carl Sagan

Before we dive into Obsidian, it’d be good to first lay out the foundations of a Personal Knowledge Management System and Zettelkasten. If you are already familiar with these terms you can skip to Section 2.

The inspiration for this section and a lot of the work on Zettelkasten is from Niklas Luhmann, an outstandingly productive sociologist who wrote 400 papers and 70 books. Zettelkasten means (literally) “slip box” (or library in this article). In his case, his Zettlekasten had around 90000 physical notes, which have been digitized and can be found here.

Nowadays, there are loads of tools available to make this process easier and more intuitive. Obsidian, specifically has a good introduction section on their website: https://publish.obsidian.md/hub/

Notes

We will start by considering “What is a note?”. Although it seems like a trivial question, the answer to this may vary depending on the topic or your style of notes. The idea, however, is that a note is as “atomic” (ie. self-contained) as possible. You should be reading the note and understand the idea immediately.

The resolution of your notes depends on how much detail you have for that note. For example, a note about “Deep Learning” could be just a general description of what Neural Networks are, and maybe a few notes on the different types of architectures (eg. Recurrent Neural Networks, Convolutional Neural Networks etc..).

A good rule of thumb to have is to limit length and detail. If you require more detail, in a specific section of this note, it would make sense to break it up into several smaller notes. So, from our original note “Deep Learning” we now have three notes:

Deep Learning

Recurrent Neural Networks

Convolutional Neural Networks

You can repeat this step however many times is necessary until you have the granularity you require. You might be tempted to place these notes into a folder called “Neural Networks”, as all the notes are about similar topics. However, there’s a slightly better strategy:

#Tags and [[Links]] over /Folders/

The main problem with using folders is that they are not versatile and they assume that all the notes contained in the folder belong uniquely to a specific category. This makes it harder for you to form connections between different topics.

For example, Deep Learning has been used for Protein Structure prediction (AlphaFold) and image classification (ImageNet). Now, if you had a folder structure like this:

- /Proteins/

- Protein Folding

- /Deep Learning/

- Convolutional Neural Networks

Your notes about Protein Folding and Convolutional Neural Networks will be independent and when you are in the “Protein” folder, you won’t be able to find notes about Neural Networks.

There are several ways to solve this problem. The most common one is to use tags rather than folders. This way, one note can be grouped with more than just one topic. Tags can also be nested (ie. have subtags) in Obsidian.

Also, you can link two notes together with links. Obsidian and some other note-taking apps let you connect one note to another, so that you can then jump to that note and build your “Knowledge Graph” as shown below:

My Knowledge Graph. Green: Biology, Red: Machine Learning, Yellow: Autoencoders, Blue: Graphs, Brown: Tags.

My Knowledge Graph and the note “Backrpropagation” and its links.

Backpropagation note and all its links

When to use Folders

Folders are however useful to organize your vault, especially as it grows. The main advice here is to have very few folders, as they should "weakly" collect groups of notes or better collect different types or sources of notes.

For example, these are the folders I use in my Zettelkasten:

The 5 folders in my Zettelkasten

They generally collect different sources of information:

MOC: Contains all the Maps of Contents to navigate the Zettelkasten.

Projects: Contains one note for each side-project of my PhD where I log my progress and ideas. These are also linked to notes.

Bio and ML: These two are essentially the main content of my Zettelkasten and they could in theory be fused into one folder.

Papers: Here I place all the notes I take from scientific papers. The notes are synced using a bibliography .bib file from Zotero.

Books: I write a note for each book I read and generally split them into multiple notes after I go through them.

Having a separate folder for images can also be a good idea, to avoid cluttering your main folders with image files.

I will discuss these more in detail in the Workflow Section.

My general suggestion for folders is to minimize them as much as possible and to use tags and links instead.

Maps of Content (MOC)

As you start growing your Zettelkasten, you might find it hard to find notes, especially when taking notes of different topics. A good solution to this is to create notes called Maps of Contents (MOCs).

These are notes that "signposts" your Zettelkasten library, directing you to the right type of notes. Inside of it you can link to other notes based on tags of a common topic. Usually this is done with a title, followed by your notes that relate to that title. This is an example:

An example of a Machine Learning MOC generated with Dataview.

As shown above, my Machine Learning MOC starts with the basics, all in one section. It then moves to Variational Auto-Encoders and Transformers. This allows you to group and quickly find all notes related to a tag without having to scroll through the tag search section.

This is why I keep MOCs at the top of my library, as I can quickly find the information I need and get a quick look at my library. These MOCs are automatically generated using an Obsidian Plugin called Dataview (https://github.com/blacksmithgu/obsidian-dataview) which works much like SQL queries.

Ideally, MOCs can be expanded and should have a bit more explanations about the notes, their status, and what you still need to do. In the absence of this, Dataview does a fantastic job at creating a good structure for your notes.

EDIT: This is the template I use for the screenshot above:

Dataview query for MOC (code)

Alternatively, this is what a book tracker looks like:

Dataview query for books in folder “4. Books”

Dataview query for books in folder “4. Books” (code)

Where each book note looks like this:

Book note with fields.

Book note with fields (code).

2. Tools: Getting to know Obsidian

Obsidian is my tool of choice as it is free, all the notes are stored in Markdown format, it can be customized/themed, and each panel can be moved around in drag and drop fashion. You can download it here: https://obsidian.md/

Interface

As I mentioned, Obsidian is very customizable, so I found this to be my optimal interface:

My interface in Obsidian. The theme is customized from https://github.com/colineckert/obsidian-things

If you want something simpler, each panel can be collapsed, moved, or removed in whatever way you wish. If you need to find a panel later on, you can click on the vertical "…" (bottom left of the note panel), and open the relevant panel.

Generally my interface is organized as such:

How my Obsidian Interface is organized.

Folders / Search: Here I have all the relevant folders. I usually use the MOC note to get to wherever I want, otherwise, I use the search button to look for a note.

Tags: I use nested tags and usually look into each of them if I am looking for specific notes to link.

cMenu: Nice plugin to place useful functionality in a handy menu (https://github.com/chetachiezikeuzor/cMenu-Plugin)

Global Graph: The graph shows all your notes (linked and unlinked). Linked notes will appear closer together. You can zoom in to read the title of each note. This can be a bit overwhelming at first, however, as your library grows, you get used to the positions and start thinking of possible connections between notes that you may not have thought about.

Local Graph: This will show your current note, in relation to other linked notes in your library. It is useful to quickly jump to another link when you need to, and go back to the current note.

Links: Finally, here I keep all the linked mentions of the notes, as well as an outline panel and the plugin Power Search (https://github.com/aviral-batra/obsidian-power-search), which allows me to search my vault by highlighting some text.

I suggest you start using the tool and then worry about positioning panels later. What works for some may not work for you so I encourage you to find the best use-case for your library.

Plugins

Another major advantage of using Obsidian is the vast choice of plugins. I use many but here are a few of the ones I use the most (Calendar, Citations, Dataview, Templater, Admonition):

Calendar: https://github.com/liamcain/obsidian-calendar-plugin

Gives you a calendar to organize your notes. This is optimal for taking notes from meetings or keeping a journal.

Calendar plugin. Image from https://github.com/hans/obsidian-citation-plugin

Citations: https://github.com/hans/obsidian-citation-plugin

Allows you to cite papers from a .bib file to include in your notes. You can also customize how your notes will be produced (eg. Title, Authors, Abstract etc..)

Citation plugin. Image from https://github.com/hans/obsidian-citation-plugin

Dataview: https://github.com/blacksmithgu/obsidian-dataview

Probably among the most powerful plugins as it allows you to query your library as a database and automatically generate content. You can see an example in the MOC section.

Templater: https://github.com/SilentVoid13/Templater

Allows you to create notes with specific templates like dates, tags, and headings.

Templater Plugin. Image from https://github.com/SilentVoid13/Templater

Admonition: https://github.com/valentine195/obsidian-admonition

Allows you to structure your notes with blocks.

Admonition plugin. Image from https://github.com/valentine195/obsidian-admonition

There are loads more plugins, but hopefully, this list will get you started on some interesting ones.

Theme (new addition)

Many have asked about my theme settings and CSS.

My CSS:

- Adds white background to all the images (which allows me to add transparent images and see them properly in dark mode)

- Leave a 40px of space between the title bar and the content

- Increase the font for LaTeX formulae

My settings for the Things theme add additional colors to the headings:

To import my theme settings you will need the plugin Style Settings: https://github.com/mgmeyers/obsidian-style-settings