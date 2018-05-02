import {
    AfterViewInit,
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
import { ImportState }             from '../../enums/import-state.enum';

import { RepositoryImportService } from '../../resources/repository-imports/repository-import.service';
import { RepositoryImport }        from '../../resources/repository-imports/repository-import';

import * as $       from 'jquery';
import * as lodash  from 'lodash';


@Component({
  selector: 'app-import-detail',
  templateUrl: './import-detail.component.html',
  styleUrls: ['./import-detail.component.less']
})
export class ImportDetailComponent implements OnInit, AfterViewInit {

    private _importTask: Import;
    private _refreshing: boolean;

    scroll: boolean = false;

    ImportState: typeof ImportState = ImportState;

    @Input()
    set importTask(data: Import) {
        if (this._importTask && this.importTask.id != data.id) {
            this.scroll = false;
            this.scrollToggled.emit(this.scroll);
        }
        this._importTask = data;
        setTimeout(_ => {
            this.affix();
        }, 1000);
    }

    get importTask(): Import {
        return this._importTask;
    }

    @Input()
    set refreshing(data: boolean) {
        this._refreshing = data;
    }

    get refreshing(): boolean {
        return this._refreshing;
    }

    @Output() startedImport = new EventEmitter<boolean>();
    @Output() scrollToggled = new EventEmitter<boolean>();

    constructor(
        private repositoryImportService: RepositoryImportService
    ) {}

    ngOnInit() {}

    ngAfterViewInit() {}

    startImport():void {
        this.repositoryImportService.save({'repository_id': this.importTask.summary_fields.repository.id})
            .subscribe(response => {
                console.log(
                  `Started import for repoostiroy ${this.importTask.summary_fields.repository.id}`
                );
                this.startedImport.emit(true);
            });
    }

    affix(): void {
        var $cache = $('#log-follow-button');
        var $idcontainer = $('#import-details-container');
        $($idcontainer).scroll(_ => {
            var y = $($idcontainer).scrollTop();
            if (y > 165) {
                $cache.addClass('fixed');
            } else {
                $cache.removeClass('fixed');
            }
        });
    }

    toggleScroll() {
        this.scroll = !this.scroll;
        this.scrollToggled.emit(this.scroll);
    }
}
