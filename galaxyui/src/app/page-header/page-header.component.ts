import {
    Component,
    OnInit,
    Input
} from '@angular/core';

class Title {
    name: string;
    path: string;
}

@Component({
  selector: 'app-page-header',
  templateUrl: './page-header.component.html',
  styleUrls: ['./page-header.component.less']
})
export class PageHeaderComponent implements OnInit {

    _headerTitle: Title[];

    @Input()
    set headerTitle(headerTitle: string) {

        // Set headerTitle to a string. For sub pages, where you want a breadcrumb trail,
        // pass a list of page names and paths separated by ';'. For example:
        // 'page_name;/path;page_name;/path/foo;page_name'.

        const title_list = headerTitle.split(';');
        this._headerTitle = [];
        title_list.forEach((item: string, idx: number) => {
            if (idx % 2) {
                const title = new Title();
                title.name = title_list[idx - 1];
                title.path = item;
                this._headerTitle.push(title);
            } else if (idx === title_list.length - 1) {
                const title = new Title();
                title.name = item;
                this._headerTitle.push(title);
            }
        });
    }

    constructor() {}

    ngOnInit() {}

}
