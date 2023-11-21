function deletePost(postId) {
    fetch('/deletepost', {
    method: 'POST',
    body: JSON.stringify({ postId: postId})
    }).then((_res) => {
        window.location.href="/post"
    });
}

function deleteComment(market_id , commentId) {
    fetch('/deletecomment', {
    method: 'POST',
    body: JSON.stringify({ commentId: commentId})
    }).then((_res) => {
        window.location.href="/market/" + market_id
    });
}

function deleteAnnouncement(market_id , announcementId) {
    fetch('/deleteannouncement', {
    method: 'POST',
    body: JSON.stringify({ announcementId: announcementId})
    }).then((_res) => {
        window.location.href="/market/" + market_id
    });
}