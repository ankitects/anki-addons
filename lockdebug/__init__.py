def closeReplacement(self, save=True):
    if self.db:
        if save:
            self.save()
        else:
            self.db.rollback()
        if not self.server:
            self.db.setAutocommit(True)

            try:
                self.db.execute("pragma journal_mode = delete")
            except Exception as e:
                if "database is locked" not in str(e):
                    raise

                try:
                    # try roll back first
                    self.db.rollback()
                    self.db.execute("pragma journal_mode = delete")
                    raise Exception("lockdebug: please let support know that attempt 1 succeeded.")
                except Exception as e:
                    if "database is locked" not in str(e):
                        raise

                    try:
                        # try close and reopen
                        self.db.close()
                        self.db = None
                        self.reopen()
                        self.db.execute("pragma journal_mode = delete")
                        raise Exception("lockdebug: please let support know that attempt 2 succeeded.")
                    except Exception as e:
                        if "database is locked" not in str(e):
                            raise

                        raise Exception("lockdebug: please let support know both attempts failed")

            self.db.setAutocommit(False)
        self.db.close()
        self.db = None
        self.media.close()
        self._closeLog()

from anki.collection import _Collection
_Collection.close=closeReplacement
