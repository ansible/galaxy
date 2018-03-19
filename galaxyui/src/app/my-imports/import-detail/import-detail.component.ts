import {
    Component,
    OnInit,
    Input
} from '@angular/core';

import {
    ImportsService,
    SaveParams
} from '../../resources/imports/imports.service';

import { Import }        from '../../resources/imports/import';
import { ImportLatest }  from '../../resources/imports/import-latest';

@Component({
  selector: 'app-import-detail',
  templateUrl: './import-detail.component.html',
  styleUrls: ['./import-detail.component.less']
})
export class ImportDetailComponent implements OnInit {

    @Input() importTask: Import;

    checking: boolean = false;

    constructor() {}

    ngOnInit() {}

}
