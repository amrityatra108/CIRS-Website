import sys,re,unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
import blog,blogposts
class LayoutTests(unittest.TestCase):
 def test_shelf(self):
  # All stories is one card per article, newest issue first, each with its picture and one way in.
  html=blog.front_html()
  shelf=html.split('data-story-list>',1)[1].split('</ul>',1)[0]
  cards=re.findall(r'<li class="ij-card".*?</li>',shelf,re.S)
  self.assertEqual([re.search(r'<h3><a href="([^"]+)\.html">',c).group(1) for c in cards],[p['slug'] for p in blogposts.by_issue()])
  for card,post in zip(cards,blogposts.by_issue()):
   self.assertIn('class="ij-card__art"',card,post['slug'])
   self.assertEqual(len(re.findall(r'<a ',card)),1,post['slug'])
  for slug in list(blog.CARD_FOCUS)+list(blog.CARD_WHOLE):self.assertIn(slug,{p['slug'] for p in blogposts.POSTS})
 def test_content_preserved(self):
  for post in blogposts.POSTS:
   self.assertIn(blog.first_sentence(blog.reading_paragraphs(post)[0]),blog.reading_paragraphs(post)[0])
   self.assertEqual(blog.display_byline(post),post['author'] or 'No byline in print')
  self.assertNotIn('existing blog credit',blog.front_html())
  self.assertNotIn('school-supplied credit',blog.front_html())
 def test_pull_quotes(self):
  # A pull quote is the article's own words, and the lead's is set beneath it.
  letters=lambda text:''.join(c for c in text.lower() if c.isalpha())
  for post in blogposts.POSTS:
   if post.get('pull_quote'):self.assertIn(letters(post['pull_quote']),letters(' '.join(blog.reading_paragraphs(post))))
  lead=blogposts.by_issue()[0]
  if lead.get('pull_quote'):self.assertIn('class="ij-lead__quote"><p>“'+blog.esc(lead['pull_quote']),blog.front_html())
if __name__=='__main__':unittest.main()
