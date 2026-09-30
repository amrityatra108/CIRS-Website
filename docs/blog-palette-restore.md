# Blog palette restoration

Restore only the Blog exception requested after undoing the local “Update page-specific colours” task. The backed-up task used paper `#F2F1ED`, ink `#161616` and burgundy `#710014` in Blog styles and the shared essay rules.

`assets/css/blog-palette.css` isolates those tokens and essay rules. The generator loads it only for Blog and its 17 student articles. School News reports also use `blog.css`, so the original shared stylesheets remain unchanged. No other palette from the rejected task is restored. Layout, article content, images and interactions stay intact.

The exact rollback backup and SHA-256 manifest remain in the local task's `evidence/page-palettes-backup` directory. Creative Writing files are untouched.
