import xlwt, xlrd

path_origin_post = '原数据/posts.xls'
path_origin_comment = '原数据/comments.xls'

path_bad_post = 'posts_bad.xls'
path_bad_comment = 'comments_bad.xls'

path_rest_post = 'posts_rest.xls'
path_rest_comment = 'comments_rest.xls'

workbook_origin_comment = xlrd.open_workbook(path_origin_comment, encoding_override="gbk")
sheet_origin_comment = workbook_origin_comment.sheet_by_index(0)
origin_comments = [[0] for i in range(sheet_origin_comment.nrows)]
for i in range(sheet_origin_comment.nrows):
#     print(sheet_origin_comment.row_values(i))
    idx, cnt, text = sheet_origin_comment.row_values(i)
    origin_comments[int(idx)].append(text)

origin_post_useful = []
origin_comment_useful = origin_comments
workbook_origin_post = xlrd.open_workbook(path_origin_post)
sheet_origin_post = workbook_origin_post.sheet_by_index(0)
for i in range(sheet_origin_post.nrows):
    if sheet_origin_post.row_values(i)[1] != '':
        origin_post_useful.append(sheet_origin_post.row_values(i))
        origin_comments[int(sheet_origin_post.row_values(i)[0])] = None

