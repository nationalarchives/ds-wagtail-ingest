from wagtail.core import blocks
from wagtail.images.blocks import ImageChooserBlock


class ParagraphWithPodcast(blocks.StructBlock):
    paragraph = blocks.RichTextBlock()
    page = blocks.PageChooserBlock()


class ContentHubBodyBlock(blocks.StreamBlock):
    paragraph_with_podcast = ParagraphWithPodcast()
