### Фиксы в мобирайзе

##### Пропадание контекста в модалках

style.css:
```
/*
.hidden {
  visibility: hidden;
}
*/
```

##### Не отображать страницу в поисковиках

```
<meta name="robots" content="noindex,follow">
```

### Деплой из мобирайза


##### Статика

Копируем в статику
```
assets
robots.txt
sitemap.xml
```

##### Формы

В файле formoid.min.js поменять урл обработки формы на
```
var API_URL = ('https:' == location.protocol ? 'https:' : 'http:') + '//api.church22.ru/api/form/';
```

##### Шаблоны

Копируем в шаблоны *.html

В шаблонах вырезаем генерируемый контент, вместо него вставляем  {{ название }}


### TODO

```
Фиксы статьи
Новости раздел
Генерация sitemap.xml
```