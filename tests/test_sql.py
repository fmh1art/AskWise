import sqlite3
import pytest
from scripts.run_e003 import execute
from scripts.audit_ambiqt import canonical,decode_text

def test_multiset_types_and_duplicate_semantics():
    assert canonical([(1,),(1,)]) != canonical([(1,)])
    assert canonical([(1,)]) != canonical([('1',)])
    assert canonical([(2,),(1,)]) == canonical([(1,),(2,)])
    assert decode_text(b'\xff') == b'\xff'

def test_generated_sql_read_only_and_one_statement():
    db=sqlite3.connect(':memory:')
    db.execute('CREATE TABLE t(x INTEGER)');db.execute('INSERT INTO t VALUES(1)')
    assert execute(db,'SELECT x FROM t') == canonical([(1,)])
    for q in ['DELETE FROM t','ATTACH DATABASE ":memory:" AS stolen','PRAGMA table_info(t)','SELECT 1; DROP TABLE t;']:
        with pytest.raises(sqlite3.Error):execute(db,q)
    assert execute(db,'SELECT x FROM t') == canonical([(1,)])
    db.close()
