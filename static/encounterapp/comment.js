if (document.readyState == "loading") {
  document.addEventListener("DOMContentLoaded", ready);
} else {
  ready();
}

function ready() {
  function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== "") {
      const cookies = document.cookie.split(";");
      for (let i = 0; i < cookies.length; i++) {
        const cookie = cookies[i].trim();
        // Does this cookie string begin with the name we want?
        if (cookie.substring(0, name.length + 1) === name + "=") {
          cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
          break;
        }
      }
    }
    return cookieValue;
  }

  const access_token = JSON.parse(
    document.getElementById("access_token").textContent
  );
  const firstname = JSON.parse(
    document.getElementById("firstname").textContent
  );
  const lastname = JSON.parse(document.getElementById("lastname").textContent);
  const userID = JSON.parse(document.getElementById("userID").textContent);
  const img = JSON.parse(document.getElementById("img").textContent);
  const token = access_token.replaceAll("-", "");

  const commentBTN = [...document.querySelectorAll(".addcomment")];
  commentBTN.forEach((value) => {
    value.addEventListener("click", function (e) {
      e.preventDefault();
      const form = e.target.closest("form");
      const formData = new FormData(form);
      const comment = formData.get("comment");
      const userid = formData.get("user");
      const postid = formData.get("post_id");
      const shared_post_id = formData.get("shared_post_id");
      const parent_id = formData.get("parent_id");
      const image = formData.get("image");
      const firstname = formData.get("firstname");
      const lastname = formData.get("lastname");
      sendComment(
        comment,
        userid,
        firstname,
        lastname,
        postid,
        image,
        parent_id,
        shared_post_id
      );
    });
  });

  const like_buttonBTN = [...document.querySelectorAll(".like-button")];
  like_buttonBTN.forEach((value) => {
    value.addEventListener("click", function (e) {
      e.preventDefault();
      const userid = e.target.dataset.userId;
      const postid = e.target.dataset.postId;
      sendLikeVideo(userid, postid);
    });
  });

  const show_commentbox = [
    ...document.querySelectorAll(".show_hide-commentbox"),
  ];
  show_commentbox.forEach((value) => {
    value.addEventListener("click", function (e) {
      e.preventDefault();

      getComments(
        e.target.dataset.itemId,
        e.target.dataset.userId,
        e.target.dataset.shareitemId
      );
    });
  });

  // ===========Socket Link=======================================
  const commentSocket = new WebSocket(
    "ws://" + window.location.host + "/ws/add_comment/" + token + "/"
  );
  // ======================ON Message========================
  commentSocket.onmessage = function (e) {
    const data = JSON.parse(e.data);
    if (data.type === "get_comment") {
      console.log(data.comment);
      displayPrevComment(data.comment);
    }
    if (data.type === "comment_message") {
      displayComment(
        data.comment,
        data.firstname,
        data.lastname,
        data.postid,
        data.image,
        data.userid,
        data.commentid,
        data.parent_id,
        data.shared_post_id
      );
      scrollToLastComment(data.postid, data.shared_post_id);
    }

    if (data.type === "delete_comment") {
      DeleteComment(data.commentid, data.userid);
    }

    if (data.type === "like_post") {
      likePost(data.postid, data.like, data.userid);
    }

    if (data.type === "like_comment") {
      likeComment(data.commentid, data.like, data.userid);
    }

    console.log(data);
  };

  function sendComment(
    comment,
    userid,
    firstname,
    lastname,
    postid,
    image,
    parent_id,
    shared_post_id
  ) {
    const data = {
      type: "comment_message",
      comment: comment,
      userid: userid,
      firstname: firstname,
      lastname: lastname,
      postid: postid,
      image: image,
      parent_id: parent_id,
      shared_post_id: shared_post_id,
    };
    console.log(data);
    commentSocket.send(JSON.stringify(data));
  }

  function sendLikeVideo(userid, postid) {
    const data = {
      type: "like_post",
      userid: userid,
      postid: postid,
    };
    commentSocket.send(JSON.stringify(data));
  }
  function sendLikeComment(userid, commentid) {
    const data = {
      type: "like_comment",
      userid: userid,
      commentid: commentid,
    };
    commentSocket.send(JSON.stringify(data));
  }

  function getComments(itemid, userid, sharedpost_id) {
    const data = {
      type: "get_comment",
      itemid: itemid,
      userid: userid,
      sharedpost_id: sharedpost_id,
    };
    console.log(data);
    commentSocket.send(JSON.stringify(data));
  }

  function deletecomment(userid, comment_id, postid, shared_post_id) {
    const data = {
      type: "delete_comment",
      userid: userid,
      comment_id: comment_id,
      postid: postid,
      shared_post_id: shared_post_id,
    };
    commentSocket.send(JSON.stringify(data));
  }

  //======================UI Display==========================================

  function displayPrevComment(comment) {
    let mainComment;
    if (comment[0].fields.post) {
      mainComment = document.querySelector(
        `[data-id="${comment[0].fields.post}"]`
      );
    }
    if (comment[0].fields.shared_post) {
      mainComment = document.querySelector(
        `[data-sharedpost-id="${comment[0].fields.shared_post}"]`
      );
    }
    mainComment.innerHTML = " ";
    comment.forEach((comment) => {
      if (comment.fields.parent === null) {
        if (mainComment) {
          const mainElement = document.createElement("div");
          mainElement.classList.add("comment_items-replies-wrap");

          const csrftoken = getCookie("csrftoken");
          const prevcomment = `   
          <div class="comment_items"  data-comment-id="${comment.pk}">
       <div class="name-img">
       <div class="author_image_wrap">
      <img
        style="border-radius: 50%;"
        alt="user-img"
        src="/media/${comment.fields.user_image}"
        class="logo__img"
      />
     </div>
     <div>
      <p> ${comment.fields.firstname} ${comment.fields.lastname} </p>
      <p>${comment.fields.created_at}</p>
      </div>
    </div>
    
      <div>
      
        <p>${comment.fields.content}</p>
        </div>
        <div class="comment_like_heart">
          
      <button type="submit" data-user-id="${userID}" data-comment-id="${comment.pk}" class="like-button-comment">&#x1F49C;</button>
      <span data-likecomment-id="${comment.pk}" class="comment_likes-count-comment">${comment.fields.likes}</span>
        </div>
  
  
    <button type="submit" data-user-id="${userID}" data-spost-id="${comment.fields.shared_post}" data-opost-id="${comment.fields.post}" data-comment-id="${comment.pk}" class="delete_comment">Delete</button>
   
     <!-- ================Replies=================== -->
  
     
    <form class="comment__form" method="POST" action="">
    <div class="author_image_wrap">
    <img
    
      style="border-radius: 50%;"
      alt="user-img"
      src="/media/${img}"
      class="logo__img"
    />
  </div>
    
    <textarea name="comment" class="comment-main-reply" placeholder="Post a Reply" rows="1" cols="25"></textarea>
    
    <input type="hidden" name="csrfmiddlewaretoken" value="${csrftoken}"/>
        <input type="hidden" name="user" value='${userID}'/>
        <input type="hidden" name="firstname" value='${firstname}'/>
        <input type="hidden" name="lastname" value='${lastname}'/>
        <input type="hidden" name="image" value='${img}'/>
        <input type="hidden" name="post_id" value='${comment.fields.post}'/>
        <input type="hidden" name="shared_post_id" value='${comment.fields.shared_post}'/>
        <input type="hidden" name="parent_id" value='${comment.pk}'/>
        <button type="submit" data-com-id="${comment.pk}" class="reply__comment">Reply</button>
      </form>
      
     </div>
    <div data-reply-id="${comment.pk}"></div>
    `;

          mainElement.innerHTML = prevcomment;

          mainComment.appendChild(mainElement);

          console.log(mainComment);
          setTimeout(() => {
            //============Like Previous DOM comment ================================
            const like_button_commentBTN = [
              ...document.querySelectorAll(".like-button-comment"),
            ];
            like_button_commentBTN.forEach((value) => {
              value.addEventListener("click", function (e) {
                e.preventDefault();

                const userid = e.target.dataset.userId;
                const commentid = e.target.dataset.commentId;
                sendLikeComment(userid, commentid);
              });
            });
            //============Delete Previous DOM comment ================================

            const delete_commentBTN = [
              ...document.querySelectorAll(".delete_comment"),
            ];
            delete_commentBTN.forEach((value) => {
              value.addEventListener("click", function (e) {
                e.preventDefault();
                console.log(e.target.dataset);
                const userid = e.target.dataset.userId;
                const postid = e.target.dataset.opostId;
                const shared_post_id = e.target.dataset.spostId;
                const comment_id = e.target.dataset.commentId;
                deletecomment(userid, comment_id, postid, shared_post_id);
              });
            });

            const comment_replyBTN = [
              ...document.querySelectorAll(`[data-com-id="${comment.pk}"]`),
            ];
            comment_replyBTN.forEach((button) => {
              button.addEventListener("click", function (e) {
                e.preventDefault();
                const form = e.target.closest("form");
                const formData = new FormData(form);
                const comment = formData.get("comment");
                const userid = formData.get("user");
                const postid = formData.get("post_id");
                const shared_post_id = formData.get("share_post_id");
                const parent_id = formData.get("parent_id");
                const image = formData.get("image");
                const firstname = formData.get("firstname");
                const lastname = formData.get("lastname");
                sendComment(
                  comment,
                  userid,
                  firstname,
                  lastname,
                  postid,
                  image,
                  parent_id,
                  shared_post_id
                );
              });
            });
          }, 2000);
        }
      }
      if (comment.fields.parent) {
        const commentDOM = [
          ...document.querySelectorAll(
            `[data-reply-id="${comment.fields.parent}"]`
          ),
        ];

        if (commentDOM) {
          const replyElement = document.createElement("div");
          replyElement.classList.add("reply-reply");
          replyElement.setAttribute("data-comment-id", `${comment.pk}`);
          const csrftoken = getCookie("csrftoken");
          const replyItem = `
          <div class="name-img">
          <div class="author_image_wrap">
         <img
           style="border-radius: 50%;"
           alt="user-img"
           src="/media/${comment.fields.user_image}"
           class="logo__img"
         />
        </div>
        <div>
         <p> ${comment.fields.firstname} ${comment.fields.lastname} </p>
         <p>${comment.fields.created_at}</p>
         </div>
       </div>
        <div>
       
          ${comment.fields.content}
       </div>
         
            <div class="like-reply">
              <span data-likecomment-id="${comment.pk}" class="reply_likes-count">${comment.fields.likes}</span>
              <button type="submit" data-user-id="${userID}" data-comment-id="${comment.pk}" class="like-button-reply">&#x1F49C;</button>
            </div>
        
  
          <button type="submit" data-user-id="${userID}" data-spost-id="${comment.fields.shared_post}" data-opost-id="${comment.fields.post}" data-comment-id="${comment.pk}"  data-delete-id="${comment.pk}" class="delete__new_comment">Delete</button>
  
        
        <!--  -->
        
      <form class="comment__form" method="POST" action="">
      <div class="author_image_wrap">
      <img
     
        style="border-radius: 50%;"
        alt="user-img"
        src="/media/${img}"
        class="logo__img"
      />
    </div>
  
      <input type="hidden" name="csrfmiddlewaretoken" value="${csrftoken}" />
  <textarea name="comment" class="comment-main-reply" placeholder="Post a Reply" rows="1" cols="25"></textarea>
      <input type="hidden" name="user" value="${userID}" />
      <input type="hidden" name="firstname" value=${firstname} />
      <input type="hidden" name="lastname" value=${lastname} />
      <input type="hidden" name="image" value=${img} />
      <input type="hidden" name="shared_post_id" value='${comment.fields.shared_post}'/>
      <input type="hidden" name="post_id" value="${comment.fields.post}" />
      <input type="hidden" name="parent_id" value="${comment.pk}" />
      
      <button type="submit" data-com-id="${comment.pk}"  class="addcomment">first</button>
    </form>
    <!--  -->
    <div class="second_level_reply">
    <div data-reply-id="${comment.pk}"></div>
    </div>
          `;

          replyElement.innerHTML = replyItem;
          commentDOM.forEach((value) => {
            value.appendChild(replyElement);
          });

          setTimeout(() => {
            // =======Delete Reply=============
            const delete_new_commentBTN = [
              ...document.querySelectorAll(`[data-delete-id="${comment.pk}"]`),
            ];

            delete_new_commentBTN.forEach((button) => {
              button.addEventListener("click", function (e) {
                e.preventDefault();

                const userid = e.target.dataset.userId;
                const comment_id = e.target.dataset.commentId;
                deletecomment(userid, comment_id);
              });
            });

            const comment_replyBTN = [
              ...document.querySelectorAll(`[data-com-id="${comment.pk}"]`),
            ];
            comment_replyBTN.forEach((button) => {
              button.addEventListener("click", function (e) {
                e.preventDefault();
                const form = e.target.closest("form");
                const formData = new FormData(form);
                const comment = formData.get("comment");
                const userid = formData.get("user");
                const postid = formData.get("post_id");
                const shared_post_id = formData.get("share_post_id");
                const parent_id = formData.get("parent_id");
                const image = formData.get("image");
                const firstname = formData.get("firstname");
                const lastname = formData.get("lastname");
                sendComment(
                  comment,
                  userid,
                  firstname,
                  lastname,
                  postid,
                  image,
                  parent_id,
                  shared_post_id
                );
              });
            });
          }, 2000);
        }
      }
    });
  }

  function displayComment(
    comment,
    firstname,
    lastname,
    postid,
    image,
    userid,
    commentid,
    parent_id,
    shared_post_id
  ) {
    if (parent_id === "") {
      console.log(shared_post_id);
      let commentList = "";
      if (postid) {
        commentList = document.querySelector(`[data-id="${postid}"]`);
      }

      if (shared_post_id) {
        commentList = document.querySelector(
          `[data-sharedpost-id="${shared_post_id}"]`
        );
      }

      if (commentList) {
        const newCommentElement = document.createElement("div");
        newCommentElement.classList.add("comment_items-replies-wrap");

        const csrftoken = getCookie("csrftoken");
        const CommentElement = `   
        <div class="comment_items"  data-comment-id="${commentid}">
     <div class="name-img">
     <div class="author_image_wrap">
    <img
    
      style="border-radius: 50%;"
      alt="user-img"
      src="/media/${image}"
      class="logo__img"
    />
   </div>
    <p> ${firstname} ${lastname} </p>
  </div>
  
    <div>
   
      <p>${comment}</p>
      </div>
      <div class="like-comment">
        <span data-likecomment-id="${commentid}" class="comment_likes-count-comment">${0}</span>
        <button type="submit" data-user-id="${userID}" data-comment-id="${commentid}"  class="like-button-comment">&#x1F49C;</button>
      </div>
  
  <div>
  <form method="POST" action="">
  <input type="hidden" name="csrfmiddlewaretoken" value="${csrftoken}" />
  <input type="hidden" name="user" value="${userID}" />
  <input type="hidden" name="comment_id" value="${commentid}" />
  <input type="hidden" name="shared_post_id" value="${shared_post_id}" />
  <input type="hidden" name="post_id" value="${postid}" />
 
  <button type="submit" data-delete-id="${commentid}" class="delete__new_comment">Delete</button>
  </form>
  </div>
   <!-- ================Replies=================== -->
  <div>
    <form class="comment__form" method="POST" action="">
    <div class="author_image_wrap">
  <img
  
    style="border-radius: 50%;"
    alt="user-img"
    src="/media/${img}"
    class="logo__img"
  />
</div>
  <textarea name="comment" class="comment-main-reply" placeholder="Post a Reply" rows="1" cols="25"></textarea>
  <input type="hidden" name="csrfmiddlewaretoken" value="${csrftoken}" />
      <input type="hidden" name="user" value='${userID}' />
      <input type="hidden" name="firstname" value=${firstname} />
      <input type="hidden" name="lastname" value=${lastname} />
      <input type="hidden" name="image" value=${img} />
      <input type="hidden" name="shared_post_id" value='${shared_post_id}'/>
      <input type="hidden" name="post_id" value='${postid}' />
     
      <input type="hidden" name="parent_id" value='${commentid}'  />
  
      <button type="submit" data-com-id="${commentid}" data-spcom-id="${shared_post_id}" class="reply__comment">Reply</button>
    </form>
  </div>
  
   </div>
  <div data-reply-id="${commentid}" data-spreply-id="${shared_post_id}"></div>
  `;
        newCommentElement.innerHTML = CommentElement;

        commentList.appendChild(newCommentElement);

        setTimeout(() => {
          // =======Delete Comment=============
          const delete_new_commentBTN = document.querySelector(
            `[data-delete-id="${commentid}"]`
          );
          delete_new_commentBTN.addEventListener("click", function (e) {
            e.preventDefault();
            const form = e.target.closest("form");
            const formData = new FormData(form);
            const userid = formData.get("user");
            const comment_id = formData.get("comment_id");
            const shared_post_id = formData.get("shared_post_id");
            const post_id = formData.get("post_id");
            deletecomment(userid, comment_id, post_id, shared_post_id);
          });

          const comment_replyBTN = document.querySelector(
            `[data-com-id="${commentid}"]`
          );
          console.log(comment_replyBTN);
          comment_replyBTN.addEventListener("click", function (e) {
            let sharedpost_id = null;
            let postid = null;
            e.preventDefault();
            const form = e.target.closest("form");
            const formData = new FormData(form);
            const comment = formData.get("comment");
            const userid = formData.get("user");
            let postID = formData.get("post_id");

            let sharedpostID = formData.get("shared_post_id");

            const parent_id = formData.get("parent_id");
            const image = formData.get("image");
            const firstname = formData.get("firstname");
            const lastname = formData.get("lastname");
            if (postID === "null") {
              postid = null;
            } else {
              postid = postID;
            }
            if (sharedpostID === "null") {
              sharedpost_id = null;
            } else {
              sharedpost_id = sharedpostID;
            }
            sendComment(
              comment,
              userid,
              firstname,
              lastname,
              postid,
              image,
              parent_id,
              sharedpost_id
            );
          });
        }, 2000);
      }
    }
    // ======First Comment End Here===========
    if (parent_id) {
      let commentDOM = "";

      if (postid) {
        commentDOM = document.querySelector(`[data-reply-id="${parent_id}"]`);
      }

      if (shared_post_id) {
        commentDOM = document.querySelector(
          `[data-spreply-id="${shared_post_id}"]`
        );
      }

      if (commentDOM) {
        const replyElement = document.createElement("div");
        replyElement.classList.add("reply-reply");
        replyElement.setAttribute("data-comment-id", `${commentid}`);
        const csrftoken = getCookie("csrftoken");
        const replyItem = `
      <div class="name-img">
      <div class="author_image_wrap">
     <img
       style="border-radius: 50%;"
       alt="user-img"
       src="/media/${image}"
       class="logo__img"
     />
    </div>
     <p> ${firstname} ${lastname} </p>
   </div>
      <div>
        ${comment}
        </div>
    
          <div class="like-reply">
            <span data-likecomment-id="${commentid}" class="reply_likes-count">${0}</span>
            <button type="submit" data-user-id="${userID}" data-comment-id="${commentid}"  class="like-button-reply">&#x1F49C;</button>
          </div>
      
      <div>
        <form  method="POST" action="">
        <input type="hidden" name="csrfmiddlewaretoken" value="${csrftoken}" />
        <input type="hidden" name="user" value="${userID}" />
        <input type="hidden" name="shared_post_id" value="${shared_post_id}" />
        <input type="hidden" name="post_id" value="${postid}" />
        <input type="hidden" name="comment_id" value="${commentid}" />
        <button type="submit" data-delete-id="${commentid}"  class="delete__new_comment">Delete</button>
      </form>
      </div>
      <!--  -->
      <div>
    <form class="comment__form" data-form-id="${commentid}"  method="POST" action="">
    <div class="author_image_wrap">
    <img
      style="border-radius: 50%;"
      alt="user-img"
      src="/media/${img}"
      class="logo__img"
    />
  </div>
    <input type="hidden" name="csrfmiddlewaretoken" value="${csrftoken}" />
<textarea name="comment" class="comment-main-reply" placeholder="Post a Reply" rows="1" cols="25"></textarea>
    <input type="hidden" name="user" value="${userID}" />
    <input type="hidden" name="firstname" value=${firstname} />
    <input type="hidden" name="lastname" value=${lastname} />
    <input type="hidden" name="image" value=${img} />
    <input type="hidden" name="shared_post_id" value='${shared_post_id}'/>
    <input type="hidden" name="post_id" value="${postid}" />
    <input type="hidden" name="parent_id" value="${commentid}" />
    </div>
    <button type="submit" data-com-id="${commentid}" data-spcom-id="${shared_post_id}" class="addcomment">first</button>
  </form>
  <!--  -->
  <div class="second_level_reply">
  <div data-reply-id="${commentid}" data-spreply-id="${shared_post_id}"></div>
  </div>
        `;

        replyElement.innerHTML = replyItem;

        commentDOM.appendChild(replyElement);

        setTimeout(() => {
          // =======Delete Reply=============
          const delete_new_commentBTN = document.querySelector(
            `[data-delete-id="${commentid}"]`
          );

          delete_new_commentBTN.addEventListener("click", function (e) {
            e.preventDefault();
            const form = e.target.closest("form");
            const formData = new FormData(form);
            const userid = formData.get("user");
            const comment_id = formData.get("comment_id");
            const shared_post_id = formData.get("shared_post_id");
            const post_id = formData.get("post_id");
            deletecomment(userid, comment_id, post_id, shared_post_id);
          });
          const comment_replyBTN = document.querySelector(
            `[data-com-id="${commentid}"]`
          );

          comment_replyBTN.addEventListener("click", function (e) {
            e.preventDefault();
            const formDOM = e.target.dataset.comId;
            const comment_form = document.querySelector(
              `[data-form-id="${formDOM}"]`
            );
            const formData = new FormData(comment_form);
            const comment = formData.get("comment");
            const userid = formData.get("user");

            const parent_id = formData.get("parent_id");
            const postid = "null" ? null : formData.get("post_id");
            const shared_post_id = "null"
              ? null
              : formData.get("shared_post_id");
            const image = formData.get("image");
            const firstname = formData.get("firstname");
            const lastname = formData.get("lastname");
            sendComment(
              comment,
              userid,
              firstname,
              lastname,
              postid,
              image,
              parent_id,
              shared_post_id
            );
          });
        }, 2000);
      }
    }
    // ======First Level Reply End Here===========
  }

  function scrollToLastComment(postid, shared_post_id) {
    let commentBox = "";
    if (postid) {
      commentBox = document.querySelector(
        `[data-item-id="${postid}"].commentbox`
      );
    }
    if (shared_post_id) {
      commentBox = document.querySelector(
        `[data-item-id="${shared_post_id}"].commentbox`
      );
    }

    const lastComment = commentBox.lastElementChild;
    lastComment.scrollIntoView({ behavior: "smooth", block: "end" });
  }

  // ==============Remove Reply From UI=================================

  function DeleteComment(commentid, userid) {
    document.querySelector(`[data-comment-id="${commentid}"]`).remove();
  }
  function likePost(postid, like, userid) {
    const likeDom = document.querySelector(`[data-likepost-id="${postid}"]`);
    likeDom.innerHTML = parseInt(likeDom.innerHTML) + like;
  }

  function likeComment(commentid, like, userid) {
    const likeDom = document.querySelector(
      `[data-likecomment-id="${commentid}"]`
    );

    likeDom.innerHTML = parseInt(likeDom.innerHTML) + like;
  }
}
