function template_news(item) {
        return `
            <div class="carousel-item ">
                <div class="media-container-row">
                    <div class="col-md-12">
                        <p class="mbr-text mbr-fonts-style status mbr-normal my-0 display-4">${item.date}</p>
                        <p class="mbr-text mbr-fonts-style status mbr-normal my-0 display-7">${item.section_title}</p>
                        <div class="wrap-img ">
                            <a href="${item.url}"><img src="${item.image}" class="img-responsive clients-img" alt="" title=""></a>
                        </div>
                        <h4 class="card-title mbr-fonts-style mbr-normal" mbr-theme-style="display-5">
                          <a href="${item.url}" class="text-secondary">${item.title}</a>
                        </h4>
                    </div>
                </div>
            </div>
`
}

$(document).ready(function () {
    console.log('request data');
    $.ajax({
        url: 'https://api.electis.ru/api/news/',
        type: 'GET',
        cache: false,
        contentType: false,
        processData: false,
        beforeSend: function (xhr) {
            xhr.setRequestHeader("Authorization", "Token 98da89c168b6e415fa6c9dcfe6230100fbf8d510");
        },
        error: function (data) {
            console.log(data);
        },
        success: function (data) {
            for (const item of data) {
                $("#news_list").append(template_news(item));
            }
            $("#news_carousel").removeData('carousel');
            $("#news_carousel").carousel("pause").removeData();
            $("#news_carousel").carousel(target_slide_index);


        },
    });
});
