function template_profile(profile) {
    var result = `
<div id="profile_id-${profile.id}" class="card py-4 col-md-12">
    <div class="card-wrapper">
        <div class="card-img">
            <img src="${profile.image}" alt="${profile.name}" title>
        </div>
        <div class="card-box">
            <div class="text-box">
                <h4 class="card-title mbr-fonts-style mbr-normal display-5">${profile.name}</h4>
                <p class="mbr-text mbr-fonts-style status mbr-normal display-4">${profile.function}</p>
                <p class="mbr-text mbr-fonts-style mbr-normal display-4">${profile.about}</p>
            </div>
            <div class="ico-wrap">`;
    if (profile.phone) result += `            
                <div class="ico-box">
                    <a href="tel:${profile.phone}"><span class="px-2 mbr-iconfont mbr-iconfont-social mbri-mobile2"></span></a>
                    <p class="mbr-text mbr-fonts-style phone mbr-normal display-4">${profile.phone}</p>
                </div>`;
    if (profile.social_email) result += `                
                <div class="ico-box">
                    <a href="mailto:${profile.social_email}"><span class="px-2 mbr-iconfont mbr-iconfont-social mbri-letter"></span></a>
                    <p class="mbr-text mbr-fonts-style phone mbr-normal display-4">${profile.social_email}</p>
                </div>`;
    if (profile.social_page) result += `                
                <div class="ico-box">
                    <a href="${profile.social_page}" target="_blank"><span class="px-2 mbr-iconfont mbr-iconfont-social mbri-link"></span></a>
                    <p class="mbr-text mbr-fonts-style phone mbr-normal display-4">${profile.social_page}</p>
                </div>`;
    result += `
                <div class="ico-box">`;
    if (profile.social_vk) result += `
                    <a href="${profile.social_vk}" target="_blank"><span class="px-2 mbr-iconfont mbr-iconfont-social socicon-vkontakte socicon"></span></a>`;
    if (profile.social_fb) result += `
                    <a href="${profile.social_fb}" target="_blank"><span class="px-2 mbr-iconfont mbr-iconfont-social socicon-facebook socicon"></span></a>`;
    if (profile.social_ok) result += `
                    <a href="${profile.social_ok}" target="_blank"><span class="px-2 mbr-iconfont mbr-iconfont-social socicon-odnoklassniki socicon"></span></a>`;
    if (profile.social_youtube) result += `
                    <a href="${profile.social_youtube}" target="_blank"><span class="px-2 mbr-iconfont mbr-iconfont-social socicon-youtube socicon"></span></a>`;
    result += `
                </div>
            </div>
        </div>
    </div>
</div>
    `;
    return result;
}

$(document).ready(function() {
    console.log('request data');
    $.ajax({
        url: 'https://api.church22.ru/api/profile/',
        type: 'GET',
//        data: form,
        cache: false,
        contentType: false,
        processData: false,
        beforeSend: function (xhr) {
            xhr.setRequestHeader ("Authorization", "Token 98da89c168b6e415fa6c9dcfe6230100fbf8d510");
        },
        error: function (data) {
            console.log(data);
        },
        success: function (data) {
            for (const profile of data) {
                $("#command_list").append(template_profile(profile));
            }
        },
    });
});
