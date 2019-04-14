import json
import os

import gdocs_converter as gconv

GDOC = {'doc_id': 'gdoc_id'}


def create_documents_dir(root):
    root.join('test.gdoc').write(json.dumps(GDOC))
    root.join('ignore.txt').write("Files that don't match won't count")

    return root


def test_all_files(tmpdir):
    documents_dir = create_documents_dir(tmpdir)

    expected_filenames = set(['test.gdoc', 'ignore.txt'])

    all_files = list(gconv.all_files(str(documents_dir)))
    filenames = set((x['filename'] for x in all_files))

    assert expected_filenames == filenames


def test_path_to_download(tmpdir):
    rootdir = str(tmpdir)
    filedct = {
        'rootpath': rootdir,
        'file_without_ext': 'test',
        'ext': 'gdoc'
    }

    expected = os.path.join(rootdir, 'test.docx')
    got = gconv.path_to_download(filedct)
    assert expected == got


def test_path_to_download_exists(tmpdir):
    rootdir = tmpdir
    filedct = {
        'rootpath': str(rootdir),
        'file_without_ext': 'test',
        'ext': 'gdoc'
    }

    rootdir.join('test.docx').write(b'Already exist')

    expected = 0
    got = gconv.path_to_download(filedct)
    assert expected == got


def test_path_to_download_no_match(tmpdir):
    rootdir = str(tmpdir)
    filedct = {
        'rootpath': rootdir,
        'file_without_ext': 'test',
        'ext': 'txt'
    }

    expected = -1
    got = gconv.path_to_download(filedct)
    assert expected == got


def test_file_id(tmpdir):
    documents_dir = create_documents_dir(tmpdir)

    expected = GDOC['doc_id']
    got = gconv.file_id(str(documents_dir.join('test.gdoc')))
    assert expected == got


def test_delete_file(tmpdir):
    filepath = tmpdir.join('test.docx')

    filepath.write('')
    assert os.path.exists(str(filepath))

    gconv.delete_file(filepath)
    assert not os.path.exists(str(filepath))
