import {
    Component,
    Input,
    OnInit 
    } from '@angular/core';

import {
    FormControl,
    Validators,
    ValidatorFn,
    AbstractControl
    } from '@angular/forms';

import { BsModalRef }              from 'ngx-bootstrap';

import { Subject }                 from 'rxjs';
import { forkJoin }                from 'rxjs/observable/forkJoin';
import { Observable }              from 'rxjs/Observable';

import { RepositoryService }       from '../../../../../resources/respositories/repository.service';
import { Repository }              from '../../../../../resources/respositories/repository';
import { RepositoryImportService } from '../../../../../resources/repository-imports/repository-import.service';


export function forbiddenCharValidator(): ValidatorFn {
    let charRE = new RegExp('[^0-9A-Za-z-_]');
    return (control: AbstractControl): { [key: string]: any } => {
        const forbidden = charRE.test(control.value);
        return forbidden ? { 'forbiddenChar': { value: control.value } } : null;
    };
}

export function forbiddenFirstCharValidator(): ValidatorFn {
    let charRE = new RegExp('^[A-Za-z0-9]');
    return (control: AbstractControl): { [key: string]: any } => {
        const forbidden = !charRE.test(control.value);
        return forbidden ? { 'forbiddenFirstChar': { value: control.value } } : null;
    };
}

export function forbiddenLastCharValidator(): ValidatorFn {
    let charRE = new RegExp('[A-Za-z0-9]$');
    return (control: AbstractControl): { [key: string]: any } => {
        const forbidden = !charRE.test(control.value);
        return forbidden ? { 'forbiddenLastChar': { value: control.value } } : null;
    };
}

@Component({
    selector: 'alternate-name-modale',
    templateUrl: './alternate-name-modal.component.html',
    styleUrls: ['./alternate-name-modal.component.less']
})
export class AlternateNameModalComponent implements OnInit {
    
    saveInProgress: boolean = false;
    repository: Repository;
    startedImport: boolean = false;

    name: FormControl = new FormControl(
        '', [
        Validators.required,
        Validators.minLength(3),
        forbiddenCharValidator(),
        forbiddenFirstCharValidator(),
        forbiddenLastCharValidator()
        ]);

    
    constructor(
        public bsModalRef: BsModalRef,
        private repositoryService: RepositoryService,
        private repositoryImportService: RepositoryImportService) {}

    ngOnInit() {
        this.name.setValue(this.repository.name);
    }

    okIsDisabled(): boolean {
        return !this.name.valid;
    }

    updateRepoName(): void {
        this.saveInProgress = true;
        if (this.name.value != this.repository.name) {
            let repo: Repository = new Repository();
            repo.id = this.repository.id;
            repo.name = this.name.value;
            repo.original_name = this.repository.original_name;
            repo.description = this.repository.description;
            repo.import_branch = this.repository.import_branch;
            repo.is_enabled = this.repository.is_enabled;
            this.repositoryService.save(repo).subscribe(_ => {
                this.repositoryImportService
                    .save({'repository_id': this.repository.id}).subscribe(_ => {
                        console.log(`Started import for ${this.repository.name}`);
                        this.saveInProgress = true;
                        this.startedImport = true;
                        this.bsModalRef.hide();
                    });
            });
        }
    }
}
