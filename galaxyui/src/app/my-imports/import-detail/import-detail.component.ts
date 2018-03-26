import {
    Component,
    EventEmitter,
    OnInit,
    Output,
    Input
} from '@angular/core';

import {
    ImportsService,
    SaveParams
} from '../../resources/imports/imports.service';

import { Import }                  from '../../resources/imports/import';
import { ImportLatest }            from '../../resources/imports/import-latest';

import { RepositoryImportService } from '../../resources/repository-imports/repository-import.service';
import { RepositoryImport }        from '../../resources/repository-imports/repository-import';

@Component({
  selector: 'app-import-detail',
  templateUrl: './import-detail.component.html',
  styleUrls: ['./import-detail.component.less']
})
export class ImportDetailComponent implements OnInit {

    @Input() importTask: Import;
    @Input() refreshing: boolean;
    @Output() startedImport = new EventEmitter<boolean>();

    checking: boolean = false;

    constructor(
        private repositoryImportService: RepositoryImportService
    ) {}

    ngOnInit() {}

    startImport():void {
        this.repositoryImportService.save({'repository_id': this.importTask.summary_fields.repository.id})
            .subscribe(response => {
                console.log(
                  `Started import for repoostiroy ${this.importTask.summary_fields.repository.id}`
                );
                this.startedImport.emit(true);
            });
    }

}
