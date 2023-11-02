function parentdir = dirname(basedir, nparents)
    if exist('nparents', 'var') == false
        nparents = 1;
    end 
    parts = regexp(basedir, '/' , 'split');
    parentdir = fullfile('/', parts{1:end-nparents});
end