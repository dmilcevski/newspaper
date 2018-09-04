# -*- coding: utf-8 -*-
"""
Output formatting to text via lxml xpath nodes abstracted in this file.
"""
__title__ = 'newspaper'
__author__ = 'Lucas Ou-Yang'
__license__ = 'MIT'
__copyright__ = 'Copyright 2014, Lucas Ou-Yang'

from html import unescape
import logging

from .text import innerTrim


log = logging.getLogger(__name__)


class OutputFormatter(object):

    def __init__(self, config):
        self.top_node = None
        self.config = config
        self.parser = self.config.get_parser()
        self.language = config.language
        self.stopwords_class = config.stopwords_class

    def update_language(self, meta_lang):
        '''Required to be called before the extraction process in some
        cases because the stopwords_class has to set incase the lang
        is not latin based
        '''
        if meta_lang:
            self.language = meta_lang
            self.stopwords_class = \
                self.config.get_stopwords_class(meta_lang)

    def get_top_node(self):
        return self.top_node

    def get_formatted(self, top_node):
        """Returns the body text of an article, and also the body article
        html if specified. Returns in (text, html) form
        """
        self.top_node = top_node
        html, text = '', ''

        self.remove_negativescores_nodes()

        if self.config.keep_article_html:
            html = self.convert_to_html()

        self.links_to_text()
        self.add_newline_to_br()
        self.add_newline_to_li()
        self.replace_with_text()
        self.remove_empty_tags()
        self.remove_trailing_media_div()
        self.remove_fewwords_paragraphs()
        self.remove_file_photo_paragraphs()
        self.remove_source_brand_from_first_sentence()

        text = self.convert_to_text()
        # print(self.parser.nodeToString(self.get_top_node()))
        return (text, html)

    def convert_to_text(self):
        txts = []
        for node in list(self.get_top_node()):
            try:
                txt = self.parser.getText(node)
            except ValueError as err:  # lxml error
                log.info('%s ignoring lxml node error: %s', __title__, err)
                txt = None

            if txt:
                txt = unescape(txt)
                txt_lis = innerTrim(txt).split(r'\n')
                txt_lis = [n.strip(' ') for n in txt_lis]
                txts.extend(txt_lis)
        return '\n\n'.join(txts)

    def convert_to_html(self):
        cleaned_node = self.parser.clean_article_html(self.get_top_node())
        return self.parser.nodeToString(cleaned_node)

    def add_newline_to_br(self):
        for e in self.parser.getElementsByTag(self.top_node, tag='br'):
            e.text = r'\n'

    def add_newline_to_li(self):
        for e in self.parser.getElementsByTag(self.top_node, tag='ul'):
            li_list = self.parser.getElementsByTag(e, tag='li')
            for li in li_list[:-1]:
                li.text = self.parser.getText(li) + r'\n'
                for c in self.parser.getChildren(li):
                    self.parser.remove(c)

    def links_to_text(self):
        """Cleans up and converts any nodes that should be considered
        text into text.
        """
        self.parser.stripTags(self.get_top_node(), 'a')

    def remove_negativescores_nodes(self):
        """If there are elements inside our top node that have a
        negative gravity score, let's give em the boot.
        """
        gravity_items = self.parser.css_select(
            self.top_node, "*[gravityScore]")
        for item in gravity_items:
            score = self.parser.getAttribute(item, 'gravityScore')
            score = float(score) if score else 0
            if score < 1:
                item.getparent().remove(item)

    def replace_with_text(self):
        """
        Replace common tags with just text so we don't have any crazy
        formatting issues so replace <br>, <i>, <strong>, etc....
        With whatever text is inside them.
        code : http://lxml.de/api/lxml.etree-module.html#strip_tags
        """
        self.parser.stripTags(
            self.get_top_node(), 'b', 'strong', 'i', 'br', 'sup')

    def remove_empty_tags(self):
        """It's common in top_node to exit tags that are filled with data
        within properties but not within the tags themselves, delete them
        """
        all_nodes = self.parser.getElementsByTags(
            self.get_top_node(), ['*'])
        all_nodes.reverse()
        for el in all_nodes:
            tag = self.parser.getTag(el)
            text = self.parser.getText(el)
            if (tag != 'br' or text != '\\r') \
                    and not text \
                    and len(self.parser.getElementsByTag(
                        el, tag='object')) == 0 \
                    and len(self.parser.getElementsByTag(
                        el, tag='embed')) == 0:
                self.parser.remove(el)

    def remove_trailing_media_div(self):
        """Punish the *last top level* node in the top_node if it's
        DOM depth is too deep. Many media non-content links are
        eliminated: "related", "loading gallery", etc
        """

        def get_depth(node, depth=1):
            """Computes depth of an lxml element via BFS, this would be
            in parser if it were used anywhere else besides this method
            """
            children = self.parser.getChildren(node)
            if not children:
                return depth
            max_depth = 0
            for c in children:
                e_depth = get_depth(c, depth + 1)
                if e_depth > max_depth:
                    max_depth = e_depth
            return max_depth

        top_level_nodes = self.parser.getChildren(self.get_top_node())
        if len(top_level_nodes) < 3:
            return

        last_node = top_level_nodes[-1]
        if get_depth(last_node) >= 2:
            self.parser.remove(last_node)

    def remove_fewwords_paragraphs(self):
        """
        Remove paragraphs that have less than x number of words,
        would indicate that it's some sort of link.
        """
        all_nodes = self.parser.getElementsByTags(self.get_top_node(), ['*'])
        all_nodes.reverse()
        for el in all_nodes:
            tag = self.parser.getTag(el)
            text = self.parser.getText(el)
            stop_words = self.stopwords_class(language=self.language). \
                get_stopword_count(text)
            if (tag != 'br' or text != '\\r') \
                    and stop_words.get_stopword_count() < 3 \
                    and len(self.parser.getElementsByTag(
                el, tag='object')) == 0 \
                    and len(self.parser.getElementsByTag(
                el, tag='embed')) == 0:
                self.parser.remove(el)
            # TODO
            # check if it is in the right place
            else:
                trimmed = self.parser.getText(el)
                if trimmed.startswith("(") and trimmed.endswith(")"):
                    self.parser.remove(el)

    def remove_file_photo_paragraphs(self):
        all_nodes = self.parser.getElementsByTags(self.get_top_node(), ['*'])
        all_nodes.reverse()
        # First remove all nodes that have tag figcaption
        for el in all_nodes:
            tag = self.parser.getTag(el)
            if(tag == 'figcaption'):
                self.parser.remove(el)

        #Then try to remove nodes that have tags with specific attibute and value
        IMAGE_CAPTION_TAGS = [
            {'attribute': 'class', 'value': 'imageCaption'},

        ]

        for known_caption_tag in IMAGE_CAPTION_TAGS:
            caption_tags = self.parser.getElementsByTag(
                self.get_top_node(),
                attr=known_caption_tag['attribute'],
                value=known_caption_tag['value'])
            if caption_tags:
                for caption_tag in caption_tags:
                    if caption_tag.attrib.get(known_caption_tag['attribute']) == known_caption_tag['value']:
                        caption_tag_node = caption_tag
                        self.parser.remove(caption_tag_node)


    def remove_source_brand_from_first_sentence(self):
        """
        Remove source brand from the first sentence.
        For example, in the sentence:
            (CNN) By the numbers, it looks like Americans are one unhealthy nation and could therefore have a lot to lose, depending on how the health care debate concludes.
        the word (CNN) should be removed.
        """
        import re
        #regex = r"(\(.*?\))"
        regex =  r"^([A-Za-z\.\s][A-Za-z\,\/\\\nd\s]+(\s+))?(\((.*?)\))?\s?[\–|\-|\—]*\s+"

        all_nodes = self.parser.getElementsByTags(self.get_top_node(), ['*'])
        for el in all_nodes:
            tag = self.parser.getTag(el)
            text = self.parser.getText(el)
            #if(tag == 'p'):
            matches = re.finditer(regex, text)

            for matchNum, match in enumerate(matches):
                # Clean the leading empty spaces or -
                text = text[(match.end()):]
                text = re.sub(r"^[\s-]+","",text)

                #If it is, start the sentence from there, and remove everything before.
                if text and text[0].istitle():
                    p = self.parser.createElement(
                        tag=tag, text=text, tail=None)
                    parent = self.parser.getParent(el)
                    self.parser.remove(el)
                    self.parser.prependChild(parent, p)
                break #stop at the first match
            break #stop at the first element