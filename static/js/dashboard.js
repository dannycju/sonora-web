$(document).ready(function() {
    $(".bookmark-title").click(function(event) {
        if ($(this).hasClass("disabled")) {
            event.preventDefault();
        }
    })

    $(".folder-title").click(function(event) {
        if ($(this).hasClass("disabled")) {
            event.preventDefault();
        }
    })
});



var disableBookmarkContainer = function(bookmarkContainer) {
    bookmarkContainer.find(".bookmark-title").addClass("disabled");
    bookmarkContainer.find(".img-doc-bookmark").addClass("doc-bookmark-disabled");
}

var enableBookmarkContainer = function(bookmarkContainer) {
    bookmarkContainer.find(".bookmark-title").removeClass("disabled");
    bookmarkContainer.find(".img-doc-bookmark").removeClass("doc-bookmark-disabled");
}

var disableFolderContainer = function(folderContainer) {
    folderContainer.find(".folder-title").addClass("disabled");
    folderContainer.find(".img-folder").addClass("folder-disabled");
}

var enableFolderContainer = function(folderContainer) {
    folderContainer.find(".folder-title").removeClass("disabled");
    folderContainer.find(".img-folder").removeClass("folder-disabled");
}

var removeBookmark = function(bookmarkId, bookmarkContainer) {
    $.ajax({
        url: "/removebookmark/" + bookmarkId + "/",
        type: "GET",
    }).done(function(response) {
        console.log("Response: " + response.message);
        if (response.message == "bookmark_removed") {
            bookmarkContainer.fadeOut(330, function() {
                bookmarkContainer.remove();
            });
        }
        else {
            enableBookmarkContainer(bookmarkContainer);
        }
    }).fail(function(xhr, status, errorThrown) {
        console.log(errorThrown);
        enableBookmarkContainer(bookmarkContainer);
    });
}

var removeFolder = function(folderId, folderContainer) {
    $.ajax({
        url: "/removefolder/" + folderId + "/",
        type: "GET",
    }).done(function(response) {
        console.log("Response: " + response.message);
        if (response.message == "folder_removed") {
            folderContainer.fadeOut(330, function() {
                folderContainer.remove();
            });
        }
        else {
            enableBookmarkContainer(folderContainer);
        }
    }).fail(function(xhr, status, errorThrown) {
        console.log(errorThrown);
        enableBookmarkContainer(folderContainer);
    });
}

$(".bookmark-container").on("click", ".item-rm-bookmark", function(event) {
    var parentBookmarkContainer = $(event.delegateTarget);
    var bookmarkId = parentBookmarkContainer.data("bookmarkId");
    var bookmarkTitle = parentBookmarkContainer.find(".bookmark-title").text();
    // console.log('Title Length: ' + bookmarkTitle.length);
    if (bookmarkTitle.length > 56) {
        bookmarkTitle = bookmarkTitle.slice(0, 42) + '...';
    }
    disableBookmarkContainer(parentBookmarkContainer);
    bootbox.confirm({
        title: 'Are you sure you want to remove "' + bookmarkTitle + '"?',
        message: 'It will be removed from your Sonora.',
        size: 'small',
        animate: false,
        closeButton: false,
        callback: function(result) {
            if (result) {
                console.log('Removing bookmark: ' + bookmarkId);
                removeBookmark(bookmarkId, parentBookmarkContainer);
            }
            else {
                enableBookmarkContainer(parentBookmarkContainer);
            }
        },
    });
});

$(".folder-container").on("click", ".item-rm-folder", function(event) {
    var parentFolderContainer = $(event.delegateTarget);
    var folderId = parentFolderContainer.data("folderId");
    var folderTitle = parentFolderContainer.find(".folder-title").text();
    if (folderTitle.length > 56) {
        folderTitle = folderTitle.slice(0, 42) + '...';
    }
    disableFolderContainer(parentFolderContainer);
    bootbox.confirm({
        title: 'Are you sure you want to remove "' + folderTitle + '"?',
        message: 'It will be removed from your Sonora together with all the bookmarks inside.',
        size: 'small',
        animate: false,
        closeButton: false,
        callback: function(result) {
            if (result) {
                console.log('Removing folder: ' + folderId);
                removeFolder(folderId, parentFolderContainer);
            }
            else {
                enableFolderContainer(parentFolderContainer);
            }
        },
    });
});



var reSets = $("#researcher-sets");
var reKeywords = reSets.data("keywords");
if (reKeywords) {
    console.log("Keywords: " + reKeywords);
    console.log("Loading researchers...")
    reSets.html('<span style="color:#757575;">Searching...</span>')
    $.ajax({
        url: "http://127.0.0.1:8000/related_researchers/?keywords=" + reKeywords,
        type: "GET",
    }).done(function(response) {
        reSets.html(response);
        console.log("Researchers loaded");
    }).fail(function(xhr, status, errorThrown) {
        qSets.html("Unable to reach resources.")
        console.log("Related Researchers: Error: " + errorThrown);
        console.log("Related Researchers: Status: " + status);
    });
}



var qSets = $("#question-sets");
var qKeywords = qSets.data("keywords");
if (qKeywords) {
    console.log("Keywords: " + qKeywords);
    console.log("Loading questions...")
    qSets.html('<span style="color:#757575;">Searching...</span>')
    $.ajax({
        url: "http://127.0.0.1:8000/related_questions/?keywords=" + qKeywords,
        type: "GET",
    }).done(function(response) {
        qSets.html(response);
        console.log("Questions loaded");
    }).fail(function(xhr, status, errorThrown) {
        qSets.html("Unable to reach resources.")
        console.log("Related Questions: Error: " + errorThrown);
        console.log("Related Questions: Status: " + status);
    });
}

var litSets = $("#lit-sets");
var litKeywords = litSets.data("keywords");

var mostCitedAction = $("#most-cited-action");
var mostRecentAction = $("#most-recent-action");

mostCitedAction.click(function() {
    if (litKeywords) {
        console.log("Keywords: " + litKeywords);
        console.log("Loading literatures...")
        mostCitedAction.addClass("active");
        mostRecentAction.removeClass("active");
        litSets.html('<span style="color:#757575;">Searching...</span>')
        $.ajax({
            url: "http://127.0.0.1:8000/related_literatures/?keywords=" + litKeywords + "&sort=cited",
            type: "GET",
        }).done(function(response) {
            litSets.html(response);
            console.log("Literatures loaded")
        }).fail(function(xhr, status, errorThrown) {
            litSets.html("Unable to reach resources.")
            console.log("Most Cited Action: Error: " + errorThrown);
            console.log("Most Cited Action: Status: " + status);
        });
    }
});
mostCitedAction.click();

mostRecentAction.click(function() {
    if (litKeywords) {
        console.log("Keywords: " + litKeywords);
        console.log("Loading literatures...")
        mostRecentAction.addClass("active");
        mostCitedAction.removeClass("active");
        litSets.html('<span style="color:#757575;">Searching...</span>')
        $.ajax({
            url: "http://127.0.0.1:8000/related_literatures/?keywords=" + litKeywords + "&sort=recent",
            type: "GET",
        }).done(function(response) {
            litSets.html(response);
            console.log("Literatures loaded")
        }).fail(function(xhr, status, errorThrown) {
            litSets.html("Unable to reach resources.")
            console.log("Most Recent Action: Error: " + errorThrown);
            console.log("Most Recent Action: Status: " + status);
        });
    }
});



function toggleShowAbstract(obj) {
    console.log(obj.innerHTML);
    if (obj.innerHTML == "Show Abstract") {
        obj.innerHTML = "Hide Abstract";
    }
    else {
        obj.innerHTML = "Show Abstract";
    }
}


function truncateBookmarkDesc() {
    $('.bookmark-desc').each(function() {
        var bookmarkDesc = $(this);
        var splitted = bookmarkDesc.text().split(' ');
        if (splitted.length > 20) {
            var html = splitted.slice(0, 19).join(' ') + '<span class="ellipsis"> ... </span>' +
                       '<button class="link link-solid-under shw-more-btn" type="button">More</button>' +
                       '<span class="desc-collapsed"> ' + splitted.slice(20).join(" ") + '</span>';
            bookmarkDesc.html(html);
        }
    });
}

function bindShowMoreAction() {
    $('.shw-more-btn').click(function() {
        var shwMoreBtn = $(this);
        var bookmarkDesc = shwMoreBtn.parent();
        bookmarkDesc.find('.desc-collapsed').removeClass('desc-collapsed');
        bookmarkDesc.find('.ellipsis').hide();
        shwMoreBtn.hide();
    });
}

function showMoreDesc(obj) {
    console.log(obj);
    obj.parent.find('.desc-collapsed').removeClass('desc-collapsed');
    obj.hide();
}

truncateBookmarkDesc();
bindShowMoreAction();

