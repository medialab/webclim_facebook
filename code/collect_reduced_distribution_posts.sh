minet ct search 'Your page has reduced distribution' \
    --start-date 2020-09-01 --end-date 2020-11-30 > \
    ./data/crowdtangle_list/reduced_distribution_posts.csv

minet ct posts-by-id post_url ./data/crowdtangle_list/self_declared_page_details.csv > \
    ./data/crowdtangle_post_by_id/screenshot_posts.csv
