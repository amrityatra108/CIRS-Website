import sys,json,subprocess,unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
import blog,bloglayout,blogposts
class LayoutTests(unittest.TestCase):
 def test_views_and_future_entries(self):
  posts=blogposts.by_issue()
  groups=[posts]+[[p for p in posts if p['section']==s] for s in {p['section'] for p in posts}]
  cases=[]
  for group in groups:
   for order in [group,list(reversed(group)),sorted(group,key=lambda p:p['title'])]:
    cases.append([blog.story_traits(p) for p in order])
  cases += [[dict(image=image,ratio=ratio,title_length=title,excerpt_length=70,minutes=3,override=override) for _ in range(n)] for n in [0,1,5,6,19,30] for image,ratio,title,override in [(True,.6,20,''),(False,1,100,'portrait'),(True,3,90,'micro'),(True,1.5,30,'wide')]]
  script="const {compose}=require('./assets/js/blog-index.js');let s='';process.stdin.on('data',c=>s+=c);process.stdin.on('end',()=>console.log(JSON.stringify(JSON.parse(s).map(compose))));"
  js=json.loads(subprocess.check_output(['node','-e',script],input=json.dumps(cases),text=True,encoding='utf-8'))
  for items,actual in zip(cases,js):
   layout,split=bloglayout.compose(items)
   self.assertEqual(actual,dict(result=layout,split=split))
   if items:self.assertEqual(layout[0]['role'],'feature')
   if split:self.assertTrue(.35<=split/len(items)<=.55)
   else:self.assertLess(len(items),6)
   used=0
   for item,entry in zip(items,layout):
    if entry['start']:used=0
    used+=entry['span'];self.assertLessEqual(used,12)
    if entry['role'] in ['portrait','strip','visual','wide']:self.assertTrue(item['image'])
    if item['title_length']>55:self.assertGreaterEqual(entry['span'],5)
 def test_content_preserved(self):
  for post in blogposts.POSTS:
   self.assertIn(blog.first_sentence(blog.reading_paragraphs(post)[0]),blog.reading_paragraphs(post)[0])
   self.assertEqual(blog.display_byline(post),post['author'] or 'No byline in print')
  self.assertNotIn('existing blog credit',blog.front_html())
  self.assertNotIn('school-supplied credit',blog.front_html())
 def test_pull_quotes(self):
  letters=lambda text:''.join(c for c in text.lower() if c.isalpha())
  for post in blogposts.POSTS:
   if post.get('pull_quote'):self.assertIn(letters(post['pull_quote']),letters(' '.join(blog.reading_paragraphs(post))))
  self.assertIn(blog.esc(blog.pull_quote(blogposts.by_issue()[0])),blog.front_html())
if __name__=='__main__':unittest.main()
