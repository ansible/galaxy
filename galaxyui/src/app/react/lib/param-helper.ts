import { cloneDeep } from 'lodash';

export class ParamHelper {
    // Helper class for managing param object.
    // Param object is just a dictionary of lists where the keys map to
    // parameter names that contain a list of values for the given parameter
    static setParam(p, key, value) {
        const params = cloneDeep(p);
        params[key] = [value];

        return params;
    }

    static appendParam(p, key, value) {
        const params = cloneDeep(p);
        if (params[key]) {
            params[key].push(value);
        } else {
            params[key] = [value];
        }

        return params;
    }

    static deleteParam(p, key, value?) {
        const params = cloneDeep(p);
        if (value && params[key].length > 1) {
            const i = params[key].indexOf(value);
            if (i !== -1) {
                params[key].splice(i, 1);
            }
        } else {
            delete params[key];
        }

        return params;
    }

    static paramExists(params, key, value) {
        if (params[key]) {
            const i = params[key].indexOf(value);
            return i !== -1;
        } else {
            return false;
        }
    }

    static getQueryString(params) {}
}
